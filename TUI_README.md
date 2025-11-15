# HyprSTT Terminal User Interface (TUI)

A modern, keyboard-driven terminal interface for HyprSTT built with [Textual](https://textual.textualize.io/).

## Features

### 📊 Dashboard
- Real-time system status monitoring
- Recording state indicator
- Whisper model status
- Transcription counter
- Audio device information
- Current timestamp

### 📜 Transcript History
- View all past transcriptions
- Timestamps for each transcription
- Automatic history persistence
- Search and browse through history
- Keeps last 100 transcriptions

### ⚙️ Configuration Editor
- Interactive YAML configuration editor
- Syntax highlighting
- Real-time validation
- Save and reload functionality
- Edit all HyprSTT settings from the TUI

### 📝 Logs Viewer
- Real-time log viewing
- Auto-scroll to latest logs
- Refresh and clear functionality
- View last 100 log entries
- Color-coded log levels

### ❓ Help System
- Built-in keyboard shortcuts reference
- Feature documentation
- Quick access with `h` or `?`

## Installation

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install textual>=0.47.0 rich>=13.7.0
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### From Source

```bash
# Install in development mode
pip install -e .

# Or run directly
./hyprstt-tui
```

## Usage

### Starting the TUI

There are multiple ways to launch the TUI:

**Option 1: Using the installed command (after pip install)**
```bash
hyprstt-tui
```

**Option 2: Using the launcher script**
```bash
./hyprstt-tui
```

**Option 3: Running directly**
```bash
python -m src.tui_controller
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `r` | Toggle recording (start/stop) |
| `q` | Quit application |
| `h` or `?` | Show help screen |
| `Tab` | Switch to next tab |
| `Shift+Tab` | Switch to previous tab |
| `Ctrl+S` | Save configuration (in Config tab) |
| `↑` / `↓` | Navigate lists and tables |
| `Enter` | Select/activate items |

### Navigation

The TUI has five main tabs:

1. **Dashboard** - Overview of system status
2. **History** - View past transcriptions
3. **Config** - Edit configuration settings
4. **Logs** - View application logs
5. **Help** - Documentation and shortcuts

Use `Tab` and `Shift+Tab` to navigate between tabs, or click on tab names with the mouse.

## Configuration

### Editing Config in TUI

1. Navigate to the **Config** tab
2. Edit the YAML configuration directly
3. Press `Ctrl+S` or click "Save Config" button
4. The configuration will be validated and saved
5. Restart HyprSTT for changes to take effect

### Config File Location

The configuration is stored at:
```
~/.config/hyprstt/config.yml
```

## Transcript History

Transcription history is automatically saved to:
```
~/.local/share/hyprstt/transcript_history.json
```

Features:
- Automatic persistence across sessions
- Timestamped entries
- Last 100 transcriptions kept
- JSON format for easy parsing

## Logs

Application logs are viewed in real-time from:
```
~/.local/share/hyprstt/logs/hyprstt.log
```

Features:
- Auto-refresh every 2 seconds
- Last 100 lines displayed
- Manual refresh and clear options
- Color-coded severity levels

## Tips & Tricks

### Running in Background

To run the TUI in the background while still using your terminal:

```bash
# Use tmux or screen
tmux new-session -s hyprstt
./hyprstt-tui
# Press Ctrl+B then D to detach

# Reattach later
tmux attach -t hyprstt
```

### Quick Recording

Press `r` from any tab to quickly toggle recording without switching to the dashboard.

### Monitoring Logs

Keep the Logs tab open to monitor real-time activity and debug issues.

### Configuration Validation

The TUI validates YAML syntax before saving. If you see an error, check:
- Proper indentation (use spaces, not tabs)
- Correct YAML syntax
- Valid configuration keys

## Troubleshooting

### TUI Won't Start

**Error: `ModuleNotFoundError: No module named 'textual'`**

Solution:
```bash
pip install textual rich
```

**Error: `No controller available`**

Solution: The controller failed to initialize. Check:
- Audio devices are available
- Dependencies are installed
- Check logs for specific errors

### Recording Not Working

1. Check the Dashboard tab for system status
2. Verify Whisper model is loaded
3. Check audio device configuration
4. Review logs for errors

### Configuration Not Saving

1. Ensure the config directory exists: `~/.config/hyprstt/`
2. Check file permissions
3. Validate YAML syntax
4. Check logs for specific errors

## Architecture

The TUI is built using:
- **Textual**: Modern TUI framework
- **Rich**: Beautiful terminal formatting
- **PyYAML**: Configuration parsing
- **JSON**: History persistence

### Components

```
HyprSTTTUI
├── StatusPanel        # Real-time status display
├── TranscriptHistory  # History viewer with persistence
├── ConfigEditor       # Interactive YAML editor
├── LogViewer          # Real-time log viewer
└── HelpPanel          # Built-in documentation
```

### Integration

The TUI integrates with `WhisperSTTController` through:
- Shared configuration
- Recording state synchronization
- Transcription callbacks
- Log file monitoring

## Future Enhancements

Potential future features:
- [ ] Audio level visualization during recording
- [ ] Statistics and analytics dashboard
- [ ] Export transcription history to various formats
- [ ] Search and filter in history
- [ ] Custom themes and color schemes
- [ ] Keyboard shortcut customization
- [ ] Multi-language support in UI
- [ ] Plugin system for extensions

## Contributing

Contributions are welcome! Areas for improvement:
- UI/UX enhancements
- Additional features
- Bug fixes
- Documentation
- Testing

## License

Same as HyprSTT - see main LICENSE file.

## Support

For issues, questions, or suggestions:
- Check the Help tab in the TUI
- Review application logs
- Open an issue on GitHub
- Consult main HyprSTT documentation
