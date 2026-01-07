"""Entry point wiring Kernel, DeterministicAgent, EntropyShield, and Axiom_UI.

This file is intentionally small. It establishes the deterministic
substrate and then hands control to the UI loop.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from kernel import Kernel, KernelConfig
from entropy_shield import EntropyShield, EntropyShieldConfig
from deterministic_agent import DeterministicAgent
from axiom_ui import run_dashboard
from logging_config import configure_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AxiomUIXV Deterministic Terminal Substrate")
    parser.add_argument("--model", default="llama3", help="Local model name exposed by Ollama")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Base URL for local Ollama API")
    parser.add_argument("--log-dir", default=".axiom_logs", help="Directory for structured logs and ledger")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    log_dir = Path(args.log_dir)
    configure_logging(run_id="axiom", log_dir=log_dir)

    shield = EntropyShield(EntropyShieldConfig(root_dir=log_dir))

    kernel = Kernel(KernelConfig(base_url=args.ollama_url, model=args.model))
    agent = DeterministicAgent(entropy_shield=shield)

    try:
        # The dashboard now wires the Entropy Shield, Kernel, and DeterministicAgent
        # together so general commands run under invariants.
        run_dashboard(shield, kernel, agent)
    finally:
        kernel.close()


if __name__ == "__main__":  # pragma: no cover
    main()
