"""Entropy_Shield module: verifiable ledger of observed state.

This module maintains the Zero Entropy Ledger, a durable record of
terminal commands, file mutations, and kernel interactions. The goal
is alignment between terminal narrative and physical file system state.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Literal, Optional

logger = logging.getLogger("tools")

EventKind = Literal["command", "file_change", "kernel_call"]


@dataclass
class LedgerEvent:
    timestamp: str
    kind: EventKind
    payload: Dict[str, Any]


@dataclass
class EntropyShieldConfig:
    root_dir: Path
    ledger_filename: str = "zero_entropy_ledger.jsonl"


class EntropyShield:
    """Deterministic audit trail for AxiomUIXV.

    Events are appended as JSON Lines. No data is discarded. This file
    is the single source of narrative state.
    """

    def __init__(self, config: EntropyShieldConfig) -> None:
        self._config = config
        self._config.root_dir.mkdir(parents=True, exist_ok=True)
        self._ledger_path = self._config.root_dir / self._config.ledger_filename
        logger.debug("EntropyShield initialized at %s", self._ledger_path)

    @property
    def ledger_path(self) -> Path:
        return self._ledger_path

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append(self, event: LedgerEvent) -> None:
        line = json.dumps(asdict(event), sort_keys=True, ensure_ascii=False)
        with self._ledger_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        logger.debug("Ledger event recorded: %s", line)

    # Public recording methods -------------------------------------------------

    def record_command(self, *, command: str, cwd: str, exit_code: Optional[int] = None) -> None:
        event = LedgerEvent(
            timestamp=self._now(),
            kind="command",
            payload={"command": command, "cwd": cwd, "exit_code": exit_code},
        )
        self._append(event)

    def record_file_change(self, *, path: Path, before_hash: Optional[str], after_hash: Optional[str]) -> None:
        event = LedgerEvent(
            timestamp=self._now(),
            kind="file_change",
            payload={
                "path": str(path),
                "before_hash": before_hash,
                "after_hash": after_hash,
            },
        )
        self._append(event)

    def record_kernel_call(self, *, prompt_hash: str, response_hash: Optional[str] = None) -> None:
        event = LedgerEvent(
            timestamp=self._now(),
            kind="kernel_call",
            payload={"prompt_hash": prompt_hash, "response_hash": response_hash},
        )
        self._append(event)

    # Simple status helpers ----------------------------------------------------

    def latest_timestamp(self) -> Optional[str]:
        """Return the timestamp of the most recent event, if any."""

        if not self._ledger_path.exists():
            return None
        last_line = None
        with self._ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
        if not last_line:
            return None
        try:
            data = json.loads(last_line)
            return data.get("timestamp")
        except json.JSONDecodeError:
            logger.warning("Failed to decode last ledger line: %s", last_line)
            return None
