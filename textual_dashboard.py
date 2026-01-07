#!/usr/bin/env python3
"""
Premium Textual TUI dashboard for AxiomUIXV.

This replaces the Rich CLI dashboard with a true terminal UI application
that renders in a borderless, sleek terminal window. Designed for Forbes-grade polish.

Run: python textual_dashboard.py
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from rich.text import Text
from textual.app import ComposeResult, RenderableType
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Static, Input
from textual.reactive import reactive
from textual.app import App
from textual.binding import Binding

from entropy_shield import EntropyShield
from kernel import Kernel
from deterministic_agent import DeterministicAgent
from law_core import law_guarded_completion

logger = logging.getLogger("axiom_tui")


@dataclass
class ThoughtEvent:
    source: str
    content: str


@dataclass
class UIState:
    thought_stream: List[ThoughtEvent] = field(default_factory=list)
    last_command: Optional[str] = None
    last_stdout: Optional[str] = None
    last_stderr: Optional[str] = None
    last_exit_code: Optional[int] = None


class ThoughtStreamWidget(Static):
    """Renders the thought stream with syntax highlighting."""

    DEFAULT_CSS = """
    ThoughtStreamWidget {
        border: solid $accent;
        height: 70%;
    }
    """

    stream: reactive[List[ThoughtEvent]] = reactive([])

    def render(self) -> RenderableType:
        from rich.table import Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Source", style="magenta", width=20)
        table.add_column("Content", style="white")
        
        for event in self.stream[-20:]:
            table.add_row(event.source, event.content[:100] + ("..." if len(event.content) > 100 else ""))
        
        return table


class StatusBarWidget(Static):
    """Shows command status and available actions."""

    DEFAULT_CSS = """
    StatusBarWidget {
        border: solid $accent;
        height: 15%;
        background: $surface;
        color: $text;
    }
    """

    command: reactive[Optional[str]] = reactive(None)
    exit_code: reactive[Optional[int]] = reactive(None)

    def render(self) -> RenderableType:
        cmd = self.command or "<no command issued>"
        code = self.exit_code if self.exit_code is not None else "—"
        hints = "[bold]!ai[/bold] for chat | [bold]!explain[/bold] to explain | [bold]!fix[/bold] to diagnose"
        
        return Text(f"Last: {cmd} | exit={code}\n{hints}", style="bold")


class InputLineWidget(Static):
    """Command input field."""

    DEFAULT_CSS = """
    InputLineWidget {
        height: 3;
        border: solid $success;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(id="command_input", placeholder="Enter command, !ai, !explain, or !fix...")


class AxiomTUI(App):
    """Forbes-grade TUI for AxiomUIXV."""

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }
    
    Header {
        background: $accent;
        color: $background;
        height: 2;
    }
    
    Footer {
        background: $accent;
        color: $background;
    }
    """

    TITLE = "AxiomUIXV — Deterministic Terminal Substrate"
    SUB_TITLE = "Forbes-grade NLP Agent with Zero Entropy Ledger"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear_stream", "Clear Stream"),
    ]

    def __init__(self, shield: EntropyShield, kernel: Kernel, agent: DeterministicAgent):
        super().__init__()
        self.shield = shield
        self.kernel = kernel
        self.agent = agent
        self.state = UIState()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield ThoughtStreamWidget(id="stream")
            yield InputLineWidget(id="input_container")
            yield StatusBarWidget(id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Set up event handlers and focus."""
        input_field = self.query_one("#command_input", Input)
        input_field.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission."""
        command = event.value.strip()
        input_field = self.query_one("#command_input", Input)
        input_field.value = ""

        if not command:
            return

        if command.lower() in {"exit", "quit"}:
            self.exit()
            return

        self.state.last_command = command
        self.state.thought_stream.append(ThoughtEvent(source="user", content=command))

        # Route commands
        if command.startswith("!ai "):
            await self._handle_ai(command[4:].strip())
        elif command == "!explain":
            await self._handle_explain()
        elif command == "!fix":
            await self._handle_fix()
        else:
            await self._handle_shell(command)

        self._update_widgets()

    async def _handle_ai(self, query: str) -> None:
        """Handle !ai <query>."""
        try:
            envelope = law_guarded_completion(kernel=self.kernel, shield=self.shield, user_content=query)
            text = str(envelope.get("payload", {}).get("text", "<no text>"))
            status = envelope.get("status", "UNKNOWN")
            self.state.thought_stream.append(
                ThoughtEvent(source=f"model[{status}]", content=text)
            )
        except Exception as exc:
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content=f"law_core: {exc}")
            )

    async def _handle_explain(self) -> None:
        """Handle !explain."""
        if not self.state.last_command:
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content="No previous command to explain.")
            )
            return

        prompt = (
            "You are a deterministic terminal assistant. Explain the following shell command "
            "and its result in clear, concise language.\n\n"
            f"Command:\n{self.state.last_command}\n"
        )
        if self.state.last_stdout:
            prompt += f"Last stdout:\n{self.state.last_stdout}\n"
        if self.state.last_stderr:
            prompt += f"Last stderr (may indicate error):\n{self.state.last_stderr}\n"

        try:
            envelope = law_guarded_completion(kernel=self.kernel, shield=self.shield, user_content=prompt)
            text = str(envelope.get("payload", {}).get("text", "<no text>"))
            status = envelope.get("status", "UNKNOWN")
            self.state.thought_stream.append(
                ThoughtEvent(source=f"model[{status}]", content=text)
            )
        except Exception as exc:
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content=f"law_core: {exc}")
            )

    async def _handle_fix(self) -> None:
        """Handle !fix."""
        if not self.state.last_command:
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content="No previous command to fix.")
            )
            return

        prompt = (
            "You are a deterministic terminal assistant. The user ran this command and it did not "
            "behave as expected. Analyze any errors and propose a single corrected command plus a brief explanation.\n\n"
            f"Command:\n{self.state.last_command}\n"
        )
        if self.state.last_stdout:
            prompt += f"Last stdout:\n{self.state.last_stdout}\n"
        if self.state.last_stderr:
            prompt += f"Last stderr (error details):\n{self.state.last_stderr}\n"

        try:
            envelope = law_guarded_completion(kernel=self.kernel, shield=self.shield, user_content=prompt)
            text = str(envelope.get("payload", {}).get("text", "<no text>"))
            status = envelope.get("status", "UNKNOWN")
            self.state.thought_stream.append(
                ThoughtEvent(source=f"model[{status}]", content=text)
            )
        except Exception as exc:
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content=f"law_core: {exc}")
            )

    async def _handle_shell(self, command: str) -> None:
        """Handle shell command execution."""
        try:
            completed = self.agent.execute_command(command, cwd=Path.cwd())
            self.state.last_stdout = completed.stdout
            self.state.last_stderr = completed.stderr
            self.state.last_exit_code = completed.returncode

            if completed.stdout:
                self.state.thought_stream.append(
                    ThoughtEvent(source="shell[stdout]", content=completed.stdout.strip()[:500])
                )
            if completed.stderr:
                self.state.thought_stream.append(
                    ThoughtEvent(source="shell[stderr]", content=completed.stderr.strip()[:500])
                )
        except Exception as exc:
            self.state.last_stderr = str(exc)
            self.state.thought_stream.append(
                ThoughtEvent(source="error", content=f"agent: {exc}")
            )

    def _update_widgets(self) -> None:
        """Refresh all widgets from state."""
        stream_widget = self.query_one("#stream", ThoughtStreamWidget)
        stream_widget.stream = self.state.thought_stream

        status_widget = self.query_one("#status", StatusBarWidget)
        status_widget.command = self.state.last_command
        status_widget.exit_code = self.state.last_exit_code

    def action_clear_stream(self) -> None:
        """Clear the thought stream."""
        self.state.thought_stream.clear()
        self._update_widgets()


def run_tui(shield: EntropyShield, kernel: Kernel, agent: DeterministicAgent) -> None:
    """Launch the Textual TUI."""
    app = AxiomTUI(shield, kernel, agent)
    app.run()
