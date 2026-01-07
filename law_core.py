"""law_core: ΛΛ Core layer for AxiomUIXV.

This module mediates all semantic calls to the local model. It applies
Axiom Hive invariants (Omega system prompt, Zero Entropy Law, Alexis
Protocol envelope) and records kernel calls in the Entropy Shield.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List

from entropy_shield import EntropyShield
from foundations import build_omega_system_prompt, build_alexis_protocol_envelope
from kernel import Kernel


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def law_guarded_completion(
    *, kernel: Kernel, shield: EntropyShield, user_content: str
) -> Dict:
    """Run a single-turn completion under the Alexis Protocol.

    The sequence is:
    - Build Omega-anchored system prompt.
    - Call the local kernel deterministically.
    - Wrap the raw text in an Alexis Protocol envelope.
    - Record prompt/response hashes in the Zero Entropy Ledger.
    """

    system_prompt = build_omega_system_prompt()
    messages: List[Dict[str, str]] = [{"role": "user", "content": user_content}]

    raw_text = kernel.generate(system_prompt=system_prompt, messages=messages)

    envelope = build_alexis_protocol_envelope(payload={"text": raw_text})

    prompt_hash = _hash_text(system_prompt + "\n" + user_content)
    response_hash = _hash_text(raw_text)
    shield.record_kernel_call(prompt_hash=prompt_hash, response_hash=response_hash)

    return envelope
