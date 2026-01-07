"""Axiom_UI module: Rich-based deterministic terminal dashboard.

The dashboard exposes three panels:
- Command line view
- Thought Stream (kernel + agent traces)
- Source of Truth status (Zero Entropy Ledger)

The tone of all messages follows the Deterministic Imperative.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from entropy_shield import EntropyShield
from law_core import law_guarded_completion
from deterministic_agent import DeterministicAgent

logger = logging.getLogger("orchestrator")

console = Console()


@dataclass
class ThoughtEvent:
    source: str
    content: str


@dataclass
class UIState:
    """Observable state for the dashboard."""

    thought_stream: List[ThoughtEvent] = field(default_factory=list)
    last_command: Optional[str] = None
    last_stdout: Optional[str] = None
    last_stderr: Optional[str] = None
    last_exit_code: Optional[int] = None


def _render_thought_stream(state: UIState) -> Panel:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Source", style="magenta", no_wrap=True)
    table.add_column("Content", style="white")

    for event in state.thought_stream[-20:]:
        table.add_row(event.source, event.content)

    return Panel(table, title="Thought Stream", border_style="cyan")


def _render_source_of_truth(shield: EntropyShield) -> Panel:
    from foundations import OMEGA_INVARIANT, ZERO_ENTROPY_LAW, SUBSTRATE_PRINCIPLE

    ledger_path = shield.ledger_path
    latest = shield.latest_timestamp() or "no events recorded yet"

    body = "\n".join(
        [
            f"Ledger: [bold]{ledger_path}[/bold]",
            f"Latest event: [green]{latest}[/green]",
            "",
            "[bold]Omega Invariant[/bold]",
            OMEGA_INVARIANT,
            "",
            "[bold]Zero Entropy Law[/bold]",
            ZERO_ENTROPY_LAW,
            "",
            "[bold]Substrate Principle[/bold]",
            SUBSTRATE_PRINCIPLE,
        ]
    )
    return Panel(body, title="Source of Truth", border_style="green")


def _render_command_view(state: UIState) -> Panel:
    cmd = state.last_command or "<no command issued>"
    status_parts = []
    if state.last_exit_code is not None:
        status_parts.append(f"exit={state.last_exit_code}")
    if state.last_stdout:
        status_parts.append("stdout✔")
    if state.last_stderr:
        status_parts.append("stderr✖")
    status = " (" + ", ".join(status_parts) + ")" if status_parts else ""
    body = f"Last command: [bold]{cmd}[/bold]{status}\n"
    body += "Type [bold]!ai[/bold] for chat, [bold]!explain[/bold] to explain last command, [bold]!fix[/bold] to diagnose errors."
    return Panel(body, title="Command Line", border_style="yellow")


def build_layout(state: UIState, shield: EntropyShield) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="upper", ratio=3),
        Layout(name="lower", ratio=1),
    )
    layout["upper"].split_row(
        Layout(name="thoughts"),
        Layout(name="source_of_truth", size=40),
    )

    layout["thoughts"].update(_render_thought_stream(state))
    layout["source_of_truth"].update(_render_source_of_truth(shield))
    layout["lower"].update(_render_command_view(state))

    return layout


def run_dashboard(shield: EntropyShield, kernel, agent: DeterministicAgent) -> None:
    """Run an interactive dashboard loop.

    The loop is intentionally simple: it reads commands from stdin,
    updates observable state, and redraws the layout. Integration with
    the DeterministicAgent and Kernel is done by the caller, which
    appends ThoughtEvents.
    """

    state = UIState()

    console.print("[bold]AxiomUIXV Deterministic Dashboard[/bold]")
    console.print("Type commands or 'exit' to leave. Execution wiring can be added in main.py.")

    with Live(build_layout(state, shield), console=console, refresh_per_second=4) as live:
        while True:
            try:
                command = console.input("[yellow]axiom> [/yellow]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[red]Session terminated by user.[/red]")
                break

            command = command.strip()
            if not command:
                continue

            if command.lower() in {"exit", "quit"}:
                console.print("[green]Deterministic session closed.[/green]")
                break

            state.last_command = command
            state.thought_stream.append(ThoughtEvent(source="user", content=command))

            # Command routing:
            # - commands starting with "!ai " go to the Lambda-Lambda Core (chat-style).
            # - "!explain" explains the last command and its output.
            # - "!fix" diagnoses the last error and proposes a corrected command.
            # - everything else is treated as a shell command executed via DeterministicAgent.
            if command.startswith("!ai "):
                query = command[4:].strip()
                try:
                    envelope = law_guarded_completion(kernel=kernel, shield=shield, user_content=query)
                    text = str(envelope.get("payload", {}).get("text", "<no text>"))
                    status = envelope.get("status", "UNKNOWN")
                    state.thought_stream.append(
                        ThoughtEvent(
                            source=f"model[{status}]",
                            content=text,
                        )
                    )
                except Exception as exc:  # deterministic failure is surfaced, not hidden
                    state.thought_stream.append(
                        ThoughtEvent(
                            source="error",
                            content=f"law_core failure: {exc}",
                        )
                    )

            elif command == "!explain":
                if not state.last_command:
                    state.thought_stream.append(
                        ThoughtEvent(source="error", content="No previous command to explain."),
                    )
                else:
                    explain_prompt = (
                        "You are a deterministic terminal assistant. Explain the following shell command "
                        "and its most recent result in clear, concise language."
                        f"\n\nCommand:\n{state.last_command}\n"
                    )
                    if state.last_stdout:
                        explain_prompt += f"\nLast stdout:\n{state.last_stdout}\n"
                    if state.last_stderr:
                        explain_prompt += f"\nLast stderr (may indicate an error):\n{state.last_stderr}\n"
                    try:
                        envelope = law_guarded_completion(kernel=kernel, shield=shield, user_content=explain_prompt)
                        text = str(envelope.get("payload", {}).get("text", "<no text>"))
                        status = envelope.get("status", "UNKNOWN")
                        state.thought_stream.append(
                            ThoughtEvent(
                                source=f"model[{status}]",
                                content=text,
                            )
                        )
                    except Exception as exc:
                        state.thought_stream.append(
                            ThoughtEvent(
                                source="error",
                                content=f"law_core failure during !explain: {exc}",
                            )
                        )

            elif command == "!fix":
                if not state.last_command:
                    state.thought_stream.append(
                        ThoughtEvent(source="error", content="No previous command to fix."),
                    )
                else:
                    fix_prompt = (
                        "You are a deterministic terminal assistant. The user ran this command and it did not "
                        "behave as expected. Analyze any errors and propose a single corrected command plus a short "
                        "explanation."
                        f"\n\nCommand:\n{state.last_command}\n"
                    )
                    if state.last_stdout:
                        fix_prompt += f"\nLast stdout:\n{state.last_stdout}\n"
                    if state.last_stderr:
                        fix_prompt += f"\nLast stderr (error details):\n{state.last_stderr}\n"
                    try:
                        envelope = law_guarded_completion(kernel=kernel, shield=shield, user_content=fix_prompt)
                        text = str(envelope.get("payload", {}).get("text", "<no text>"))
                        status = envelope.get("status", "UNKNOWN")
                        state.thought_stream.append(
                            ThoughtEvent(
                                source=f"model[{status}]",
                                content=text,
                            )
                        )
                    except Exception as exc:
                        state.thought_stream.append(
                            ThoughtEvent(
                                source="error",
                                content=f"law_core failure during !fix: {exc}",
                            )
                        )

            else:
                # Treat everything else as a shell command to be executed deterministically.
                try:
                    completed = agent.execute_command(command, cwd=Path.cwd())
                    state.last_stdout = completed.stdout
                    state.last_stderr = completed.stderr
                    state.last_exit_code = completed.returncode

                    if completed.stdout:
                        state.thought_stream.append(
                            ThoughtEvent(
                                source="shell[stdout]",
                                content=completed.stdout.strip(),
                            )
                        )
                    if completed.stderr:
                        state.thought_stream.append(
                            ThoughtEvent(
                                source="shell[stderr]",
                                content=completed.stderr.strip(),
                            )
                        )
                except Exception as exc:
                    state.last_stderr = str(exc)
                    state.last_exit_code = None
                    state.thought_stream.append(
                        ThoughtEvent(
                            source="error",
                            content=f"deterministic agent failure: {exc}",
                        )
                    )

            live.update(build_layout(state, shield))
