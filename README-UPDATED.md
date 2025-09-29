# HyprSTT

A Speech-to-Text application designed to work with Hyprland and other Wayland compositors on Linux. Records audio on hotkey press, transcribes it using OpenAI's Whisper model, and copies the transcribed text to the clipboard.

## Features

- Speech-to-text transcription using Whisper models (tiny to large)
- Hotkey-triggered recording (configurable)
- Visual recording indicator
- Clipboard-based text output with notifications
- Low-latency transcription with optimized performance
- Support for Hyprland and other Wayland compositors

## Requirements

- Python 3.8 or newer
- Linux with Wayland (tested with Hyprland)
- A microphone
- wl-clipboard (for clipboard operations)
- notify-send (for notifications)

## Quick Setup

Use the provided quick setup script to install all dependencies and prepare the environment:

```bash
./quick-setup.sh
```

This will:
1. Create a Python virtual environment
2. Install required packages
3. Download the specified Whisper model
4. Create necessary directories

## Manual Installation

If you prefer manual installation:

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Set up the configuration:
   ```bash
   # Configuration file is at config/config.yml
   # Modify settings as needed
   ```

## Usage

1. Start the application:
   ```bash
   ./run.sh
   ```

   For development/debugging mode:
   ```bash
   ./run-dev.sh
   ```

2. Press the configured hotkey (default: F9) to start recording
3. Speak clearly into your microphone
4. Press the hotkey again to stop recording
5. The transcribed text will be copied to your clipboard and a notification will appear
6. Paste the text wherever you need it

## Configuration

Edit the `config/config.yml` file to customize:

- Whisper model size and parameters
- Audio recording settings
- Hotkey combinations
- Visual indicators and notifications

Example configuration:
```yaml
audio:
  rate: 16000
  chunk: 4096
  channels: 1
  max_duration: 0  # 0 for unlimited

whisper:
  model_size: "medium"  # tiny, base, small, medium, large
  device: "auto"  # cpu, cuda, auto
  compute_type: "float32"
  language: "en"
  models_dir: "~/.cache/whisper"

hotkeys:
  toggle_recording: ["F9"]  # Hotkey combination
  use_hypr_dispatch: false  # Use Hyprland IPC

ui:
  notifications: true
  notification_timeout: 2
  visual_indicator:
    enabled: true
    type: "overlay"
    position: "top-right"
    size: "medium"
    color: "#ff0000"
    opacity: 0.8
    pulse: true
```

## Advanced Configuration

### Custom Hyprland Binding

For more reliable hotkey detection, add this to your Hyprland config:

```
bind = SUPER, SPACE, exec, /path/to/hyprstt/toggle-stt.sh
```

### Using Different Models

Choose from different Whisper model sizes for varying accuracy and speed:
- `tiny`: Fastest, least accurate
- `base`: Fast, reasonable accuracy
- `small`: Good balance of speed and accuracy
- `medium`: Better accuracy, slower
- `large`: Best accuracy, but slowest and requires more resources

## Troubleshooting

### Application Logs

Log files are stored at:
```
~/.local/share/whisper-stt/logs/whisper_stt.log
```

### Failed Transcription Debugging

When transcription fails, audio is saved for debugging:
```
~/.local/share/whisper-stt/debug/failed_audio_*.wav
```

### Common Issues

- **Audio Not Recognized**: Try speaking louder or adjusting microphone settings
- **Hotkey Not Working**: Check for conflicts with other applications
- **Clipboard Issues**: Make sure wl-clipboard is installed

## Customization

For advanced customization options, see `CUSTOMIZATION.md` for guidance on modifying the codebase.

## License

[MIT License](LICENSE)

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [Hyprland](https://github.com/hyprwm/Hyprland)