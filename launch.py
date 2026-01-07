#!/usr/bin/env python3
"""Desktop launcher wrapper for AxiomUIXV

Run this file to start the AxiomUIXV deterministic terminal dashboard.
Works when launched from desktop shortcut, command palette, or anywhere.

The wrapper sets up minimal environment and forwards to main.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
MAIN_PATH = THIS_DIR / "main.py"


def main() -> None:
    # Ensure we can import local modules
    if str(THIS_DIR) not in sys.path:
        sys.path.insert(0, str(THIS_DIR))

    if not MAIN_PATH.is_file():
        print(f"AxiomUIXV entry point not found at: {MAIN_PATH}", file=sys.stderr)
        sys.exit(1)

    # Import core modules for TUI
    from main import parse_args, configure_logging
    from kernel import Kernel, KernelConfig
    from entropy_shield import EntropyShield, EntropyShieldConfig
    from deterministic_agent import DeterministicAgent
    from textual_dashboard import run_tui

    args = parse_args()
    log_dir = Path(args.log_dir)
    configure_logging(run_id="axiom", log_dir=log_dir)

    shield = EntropyShield(EntropyShieldConfig(root_dir=log_dir))
    kernel = Kernel(KernelConfig(base_url=args.ollama_url, model=args.model))
    agent = DeterministicAgent(entropy_shield=shield)

    try:
        run_tui(shield, kernel, agent)
    finally:
        kernel.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[red]Interrupted by user.[/red]", file=sys.stderr)
    except Exception as exc:
        print(f"[red]Fatal error in launcher: {exc}[/red]", file=sys.stderr)
        sys.exit(1)