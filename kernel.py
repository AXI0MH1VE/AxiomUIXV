"""Kernel module: local-only interface to the Ollama HTTP API.

This module is the deterministic substrate for all language model
interaction. It never sends data off the local host and assumes
Ollama is running on the same machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
import logging

logger = logging.getLogger("ollama")


@dataclass
class KernelConfig:
    """Configuration for the local inference kernel.

    The kernel speaks HTTP to a locally running Ollama instance.
    All data remains on this machine.
    """

    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    request_timeout: float = 120.0


class Kernel:
    """Deterministic interface over the Ollama HTTP API.

    This class exposes a small, explicit surface area for the rest
    of the system. It does not hide network errors and does not
    retry silently. Callers must handle failures explicitly.
    """

    def __init__(self, config: Optional[KernelConfig] = None) -> None:
        self.config = config or KernelConfig()
        self._client = httpx.Client(base_url=self.config.base_url, timeout=self.config.request_timeout)
        logger.debug("Kernel initialized with base_url=%s model=%s", self.config.base_url, self.config.model)

    def close(self) -> None:
        self._client.close()
        logger.debug("Kernel HTTP client closed")

    def generate(
        self,
        *,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call the local model deterministically.

        Arguments:
            system_prompt: The non-negotiable instruction anchor.
            messages: Conversation messages (role + content).
            temperature: Kept at or near zero to enforce stability.
            max_tokens: Optional upper bound on generated tokens.
        """

        payload: Dict[str, Any] = {
            "model": self.config.model,
            "options": {
                "temperature": temperature,
            },
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages,
            ],
        }

        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        logger.debug("Kernel.generate payload=%s", payload)

        response = self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        logger.debug("Kernel.generate raw_response=%s", data)

        # Minimal schema assumption compatible with Ollama's chat endpoint.
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Unexpected kernel response structure: %s", data)
            raise RuntimeError("Kernel response shape mismatch") from exc

        return content
