"""
HyprSTT TUI - Terminal User Interface using Textual
"""
import os
import sys
import time
import json
import yaml
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Button, Label,
    DataTable, Log, TabbedContent, TabPane,
    Input, TextArea, Switch, Select
)
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.syntax import Syntax

from .utils import setup_logger, get_config_path

logger = setup_logger("hyprstt.tui")


class StatusPanel(Static):
    """Display current system status"""

    recording = reactive(False)
    last_transcription = reactive("")
    transcription_count = reactive(0)
    model_loaded = reactive(False)
    audio_device = reactive("Unknown")

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

    def compose(self) -> ComposeResult:
        yield Static(id="status-content")

    def on_mount(self) -> None:
        self.update_status()
        self.set_interval(1.0, self.update_status)

    def update_status(self) -> None:
        """Update status display"""
        if self.controller:
            self.recording = self.controller.is_recording
            self.model_loaded = self.controller.whisper_processor is not None

        # Build status panel
        status_table = RichTable.grid(padding=(0, 2))
        status_table.add_column(style="bold cyan")
        status_table.add_column()

        # Recording status
        rec_status = "[bold red]RECORDING[/]" if self.recording else "[green]Idle[/]"
        status_table.add_row("Status:", rec_status)

        # Model status
        model_status = "[green]Loaded[/]" if self.model_loaded else "[yellow]Not loaded[/]"
        status_table.add_row("Whisper Model:", model_status)

        # Transcription count
        status_table.add_row("Transcriptions:", str(self.transcription_count))

        # Last transcription
        if self.last_transcription:
            preview = (self.last_transcription[:50] + "...") if len(self.last_transcription) > 50 else self.last_transcription
            status_table.add_row("Last:", preview)

        # Audio device
        status_table.add_row("Audio Device:", self.audio_device)

        # Current time
        status_table.add_row("Time:", datetime.now().strftime("%H:%M:%S"))

        panel = Panel(
            status_table,
            title="[bold]System Status[/]",
            border_style="blue"
        )

        self.query_one("#status-content", Static).update(panel)

    def update_transcription(self, text: str) -> None:
        """Update with new transcription"""
        self.last_transcription = text
        self.transcription_count += 1
        self.update_status()


class TranscriptHistory(Static):
    """Display transcript history"""

    def __init__(self):
        super().__init__()
        self.history_file = os.path.expanduser("~/.local/share/hyprstt/transcript_history.json")
        self.transcripts = self.load_history()

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield DataTable(id="transcript-table")

    def on_mount(self) -> None:
        table = self.query_one("#transcript-table", DataTable)
        table.add_columns("Time", "Transcription")
        table.cursor_type = "row"

        for transcript in reversed(self.transcripts[-50:]):  # Show last 50
            table.add_row(
                transcript.get("timestamp", "Unknown"),
                transcript.get("text", "")
            )

    def load_history(self) -> List[Dict[str, str]]:
        """Load transcript history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
        return []

    def save_history(self) -> None:
        """Save transcript history to file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.transcripts, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_transcript(self, text: str) -> None:
        """Add new transcript to history"""
        transcript = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": text
        }
        self.transcripts.append(transcript)
        self.save_history()

        # Update table
        table = self.query_one("#transcript-table", DataTable)
        table.add_row(transcript["timestamp"], text)

        # Keep only last 100 in memory
        if len(self.transcripts) > 100:
            self.transcripts = self.transcripts[-100:]


class ConfigEditor(Static):
    """Interactive configuration editor"""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        self.config_path = config_path or get_config_path()
        self.config = self.load_config()

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Configuration Editor", classes="section-title")
            yield Label("Edit config.yml settings (Ctrl+S to save)", classes="help-text")
            yield TextArea(id="config-editor", language="yaml")
            yield Horizontal(
                Button("Save Config", variant="primary", id="save-config"),
                Button("Reload Config", variant="default", id="reload-config"),
                classes="button-row"
            )

    def on_mount(self) -> None:
        editor = self.query_one("#config-editor", TextArea)
        editor.load_text(yaml.dump(self.config, default_flow_style=False, sort_keys=False))

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        return {}

    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            editor = self.query_one("#config-editor", TextArea)
            config_text = editor.text

            # Validate YAML
            config_data = yaml.safe_load(config_text)

            # Save to file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                f.write(config_text)

            self.config = config_data
            self.app.notify("Configuration saved successfully!", severity="information")
            return True
        except yaml.YAMLError as e:
            self.app.notify(f"Invalid YAML: {e}", severity="error")
            return False
        except Exception as e:
            self.app.notify(f"Failed to save config: {e}", severity="error")
            logger.error(f"Failed to save config: {e}")
            return False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "save-config":
            self.save_config()
        elif event.button.id == "reload-config":
            self.config = self.load_config()
            editor = self.query_one("#config-editor", TextArea)
            editor.load_text(yaml.dump(self.config, default_flow_style=False, sort_keys=False))
            self.app.notify("Configuration reloaded", severity="information")


class LogViewer(Static):
    """View application logs"""

    def __init__(self):
        super().__init__()
        self.log_file = os.path.expanduser("~/.local/share/hyprstt/logs/hyprstt.log")

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Application Logs", classes="section-title")
            yield Log(id="log-display", auto_scroll=True)
            yield Horizontal(
                Button("Refresh", variant="primary", id="refresh-logs"),
                Button("Clear Display", variant="default", id="clear-logs"),
                classes="button-row"
            )

    def on_mount(self) -> None:
        self.load_logs()
        self.set_interval(2.0, self.load_logs)

    def load_logs(self) -> None:
        """Load and display logs"""
        try:
            if os.path.exists(self.log_file):
                log_widget = self.query_one("#log-display", Log)

                # Read last 100 lines
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:]

                    # Only add new lines
                    if not hasattr(self, '_last_line_count'):
                        self._last_line_count = 0

                    new_lines = recent_lines[self._last_line_count:]
                    for line in new_lines:
                        log_widget.write_line(line.rstrip())

                    self._last_line_count = len(recent_lines)
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "refresh-logs":
            self._last_line_count = 0
            log_widget = self.query_one("#log-display", Log)
            log_widget.clear()
            self.load_logs()
            self.app.notify("Logs refreshed", severity="information")
        elif event.button.id == "clear-logs":
            log_widget = self.query_one("#log-display", Log)
            log_widget.clear()
            self._last_line_count = 0
            self.app.notify("Display cleared", severity="information")


class HelpPanel(Static):
    """Display help information"""

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static(id="help-content")

    def on_mount(self) -> None:
        help_text = """
[bold cyan]HyprSTT Terminal User Interface[/]

[bold yellow]Keyboard Shortcuts:[/]
  [bold]r[/]         - Toggle recording (start/stop)
  [bold]q[/]         - Quit application
  [bold]h[/] or [bold]?[/]  - Show this help
  [bold]Ctrl+S[/]    - Save configuration (in Config tab)
  [bold]Tab[/]       - Switch between tabs
  [bold]Shift+Tab[/] - Switch tabs (reverse)

[bold yellow]Tabs:[/]
  [bold]Dashboard[/]     - System status and overview
  [bold]History[/]       - View past transcriptions
  [bold]Config[/]        - Edit configuration settings
  [bold]Logs[/]          - View application logs
  [bold]Help[/]          - This help screen

[bold yellow]Features:[/]
  • Real-time status monitoring
  • Transcript history with timestamps
  • Interactive configuration editor
  • Live log viewing
  • Keyboard-driven interface

[bold yellow]About:[/]
  HyprSTT is a speech-to-text application for Hyprland/Wayland
  using OpenAI's Whisper model for local transcription.

  For more information, visit the documentation or GitHub repository.
"""
        panel = Panel(
            help_text,
            title="[bold]Help & Documentation[/]",
            border_style="green"
        )
        self.query_one("#help-content", Static).update(panel)


class HyprSTTTUI(App):
    """HyprSTT Terminal User Interface"""

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $accent;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    .help-text {
        color: $text-muted;
        margin-bottom: 1;
    }

    .button-row {
        height: auto;
        margin: 1 0;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }

    DataTable {
        height: 100%;
    }

    #status-content {
        height: auto;
        padding: 1;
    }

    #config-editor {
        height: 30;
        margin: 1 0;
    }

    #log-display {
        height: 100%;
        border: solid $accent;
        margin: 1 0;
    }

    TabbedContent {
        height: 100%;
    }

    TabPane {
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "toggle_recording", "Record", priority=True),
        Binding("h", "show_help", "Help"),
        Binding("?", "show_help", "Help"),
    ]

    TITLE = "HyprSTT - Speech to Text"

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.status_panel = None
        self.history_panel = None

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()

        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                self.status_panel = StatusPanel(self.controller)
                yield self.status_panel

            with TabPane("History", id="history"):
                self.history_panel = TranscriptHistory()
                yield self.history_panel

            with TabPane("Config", id="config"):
                yield ConfigEditor()

            with TabPane("Logs", id="logs"):
                yield LogViewer()

            with TabPane("Help", id="help"):
                yield HelpPanel()

        yield Footer()

    def action_toggle_recording(self) -> None:
        """Toggle recording via controller"""
        if self.controller:
            self.controller._toggle_recording()
            self.notify(
                "Recording..." if self.controller.is_recording else "Stopped",
                severity="information"
            )
        else:
            self.notify("No controller available", severity="warning")

    def action_show_help(self) -> None:
        """Switch to help tab"""
        tabs = self.query_one(TabbedContent)
        tabs.active = "help"

    def on_transcription_complete(self, text: str) -> None:
        """Handle completed transcription"""
        if self.status_panel:
            self.status_panel.update_transcription(text)
        if self.history_panel:
            self.history_panel.add_transcript(text)
        self.notify(f"Transcribed: {text[:50]}...", timeout=5)


def run_tui(controller=None):
    """Run the TUI application"""
    app = HyprSTTTUI(controller=controller)
    return app.run()
