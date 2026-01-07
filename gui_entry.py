#!/usr/bin/env python3
"""GUI entry for AxiomUIXV — wraps the console CLI to avoid a flashing console.

- On Windows: attaches to its parent console if one exists (so stdin/stdout still work),
  otherwise launches the CLI in a hidden console.
- On other platforms: transparently forwards to main.py.
"""

from __future__ import annotations

import os
import sys
import subprocess
import ctypes
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
MAIN_PATH = THIS_DIR / "main.py"


def has_console() -> bool:
    """Return True if this process is already attached to a console."""
    # Windows only: ctypes detection of console attachment.
    if sys.platform == "win32":
        return bool(ctypes.windll.kernel32.GetConsoleWindow())
    return sys.__stdout__ is not None and sys.__stdout__.isatty()


def run_in_new_console() -> None:
    """Launch main.py in a new console window (visible)."""
    exe = sys.executable
    subprocess.Popen([exe, str(MAIN_PATH)] + sys.argv[1:], cwd=THIS_DIR)


def run_hidden_console() -> None:
    """Fallback: always launch visible console to preserve Rich UI."""
    exe = sys.executable
    subprocess.Popen([exe, str(MAIN_PATH)] + sys.argv[1:], cwd=THIS_DIR)


def main() -> None:
    # Ensure local modules can be imported
    if str(THIS_DIR) not in sys.path:
        sys.path.insert(0, str(THIS_DIR))

    if not MAIN_PATH.is_file():
        print(f"[red]AxiomUIXV entry point not found at: {MAIN_PATH}[/red]", file=sys.stderr)
        sys.exit(1)

    # If there is an existing console, just invoke main directly.
    if has_console():
        from main import main as actual_main
        actual_main()
        return

    # On Windows with no console: try launching hidden.
    # If the user explicitly asks for a console (--console), launch visible.
    if "--console" in sys.argv:
        run_in_new_console()
        return

    # Always run in a visible console; Rich + Live requires a terminal.
    run_in_new_console()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"[red]Fatal error in GUI entry: {exc}[/red]", file=sys.stderr)
        sys.exit(1)