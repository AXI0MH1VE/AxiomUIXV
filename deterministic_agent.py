"""Deterministic_Agent module: invariant-checked execution.

The DeterministicAgent inspects every proposed action against explicit
safety invariants before allowing execution. There is no blind trust
in free-form suggestions.
"""

from __future__ import annotations

import logging
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Protocol

from entropy_shield import EntropyShield

logger = logging.getLogger("agent")


class Invariant(Protocol):
    """Protocol for safety invariants applied to shell commands."""

    def validate(self, tokens: List[str]) -> None:
        """Raise an exception if the invariant is violated."""


@dataclass
class ForbiddenCommandInvariant:
    forbidden_tokens: Iterable[str]

    def validate(self, tokens: List[str]) -> None:  # type: ignore[override]
        lowered = {t.lower() for t in tokens}
        for forbidden in self.forbidden_tokens:
            if forbidden.lower() in lowered:
                raise RuntimeError(f"Command violates deterministic safety invariant: token '{forbidden}' is forbidden")


class DeterministicAgent:
    """Agent that only executes commands after invariant verification.

    This class is the first concrete layer of the Zero Entropy
    Execution Framework (ZEEF) in this environment. It enforces a
    simple Deterministic Coherence Gate (DCG): commands that are
    ambiguous, dangerous, or unverifiable at this layer are halted
    instead of "best-effort" executed.
    """

    def __init__(
        self,
        *,
        entropy_shield: EntropyShield,
        invariants: Iterable[Invariant] | None = None,
    ) -> None:
        self._entropy_shield = entropy_shield
        self._invariants: List[Invariant] = list(invariants or [
            ForbiddenCommandInvariant(forbidden_tokens=["rm", "rm -rf", "shutdown", "reboot", "format"]),
        ])

    # Deterministic Coherence Gate ---------------------------------------------

    def _coherence_gate(self, tokens: List[str]) -> None:
        """Apply lightweight DCG checks before execution.

        This is a practical approximation of the full DCG described in
        Axiom Hive. It encodes "no opaque, irreversible actions" as a
        local rule. If the command is empty or obviously unsafe, we
        raise and prefer halt over drift.
        """

        if not tokens:
            raise RuntimeError("DCG: empty command rejected (ZEL: nothing to prove)")

        # Extremely conservative: block shell metacharacters that would
        # make reasoning about the command non-local.
        joined = " ".join(tokens)
        for ch in ["|", "&", ";", "&&", "||"]:
            if ch in joined:
                raise RuntimeError(f"DCG: metacharacter '{ch}' rejected under Zero Entropy Law")

    # Command path -------------------------------------------------------------

    def verify_command(self, command: str) -> List[str]:
        """Tokenize and verify a shell command.

        This call is pure: it does not execute anything. It only raises
        if an invariant is broken.
        """

        tokens = shlex.split(command, posix=False)
        logger.debug("Verifying command tokens=%s", tokens)

        for invariant in self._invariants:
            invariant.validate(tokens)

        # Deterministic Coherence Gate: final local safety pass.
        self._coherence_gate(tokens)

        return tokens

    def execute_command(self, command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        """Execute a previously verified command and record it in the ledger.

        The Zero Entropy Law is enforced at this layer: if verification
        fails, execution is blocked and no side effects occur.
        """

        tokens = self.verify_command(command)
        logger.info("Executing verified command: %s", command)

        completed = subprocess.run(
            tokens,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            shell=False,
        )

        self._entropy_shield.record_command(command=command, cwd=str(cwd), exit_code=completed.returncode)

        logger.debug("Command stdout=%s", completed.stdout)
        logger.debug("Command stderr=%s", completed.stderr)
        return completed

    # File mutation path -------------------------------------------------------

    def write_file(self, path: Path, content: str) -> None:
        """Write a file deterministically and record the change.

        This helper computes hashes before and after, and routes the
        event into the Entropy Shield.
        """

        before_hash = self._safe_hash(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        after_hash = self._safe_hash(path)

        self._entropy_shield.record_file_change(path=path, before_hash=before_hash, after_hash=after_hash)

    @staticmethod
    def _safe_hash(path: Path) -> str | None:
        import hashlib

        if not path.exists():
            return None
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()
