# Hyprland Whisper STT - Usage Guide

## Basic Usage

1. Start the service with `./run-dev.sh` (for development/debugging) or `./run.sh` (for regular use)
2. Press F9 to start recording (or Super+Space if using Hyprland event socket)
3. Speak clearly into your microphone
4. Press F9 again to stop recording and process the speech
5. The transcribed text will be injected into the currently focused window

## Visual Indicator

When recording is active, a visual indicator will appear on screen (by default in the top-right corner). This helps you know when the system is actively listening.

## Configuration

You can customize the behavior by editing `config/config.yml`:

```yaml
audio:
  rate: 16000  # Sample rate (Hz)
  chunk: 4096  # Buffer size
  channels: 1  # Mono audio
  max_duration: 30  # Maximum recording duration in seconds (0 for unlimited)

whisper:
  model_size: "small"  # Options: tiny, base, small, medium, large
  device: "auto"  # Options: cpu, cuda, auto
  compute_type: "float32"  # Options: float16, float32, int8
  language: "en"  # Language code (leave empty for auto-detect)
  models_dir: "~/.cache/whisper"  # Directory to store models

hotkeys:
  toggle_recording: ["F9"]  # Hotkey combination
  use_hypr_dispatch: false  # Use Hyprland IPC for hotkey detection

ui:
  notifications: true  # Enable desktop notifications
  notification_timeout: 2  # Notification display time in seconds
  visual_indicator:
    enabled: true  # Show visual indicator when recording
    type: "overlay"  # Indicator type: overlay, border, icon
    position: "top-right"  # Position options: top-left, top-right, bottom-left, bottom-right, top-center, bottom-center
    size: "medium"  # Size options: small, medium, large
    color: "#ff0000"  # Color in hex format
    opacity: 0.8  # Opacity (0.0-1.0)
    pulse: true  # Enable pulsing effect
```

## Troubleshooting

### Speech Not Recognized

If your speech isn't being recognized:
- Try speaking for at least 2-3 seconds
- Speak clearly and at a normal pace
- Check that your microphone is working properly
- Try using a larger model size in the config (e.g., "medium" instead of "small")

### Hotkey Not Working

If the hotkey isn't working:
- Check if there's a conflict with another application using the same key
- Try setting up a direct binding in your Hyprland config:
  ```
  bind = SUPER, SPACE, exec, /path/to/hyprland-whisper-stt/toggle-stt.sh
  ```

### Visual Indicator Not Appearing

If the visual indicator isn't showing:
- Make sure the `enabled` option is set to `true` in the config
- Try changing the position or size to make it more visible
- Check that kitty terminal is installed (used to create the overlay)

## Advanced Usage

### Custom Hyprland Binding

You can set up a direct Hyprland binding by adding this to your Hyprland config:

```
bind = SUPER, SPACE, exec, /path/to/hyprland-whisper-stt/toggle-stt.sh
```

This will use a signal to toggle recording state, which can be more reliable than the built-in hotkey detection.

### Changing Models

If you need better accuracy, try using a larger model by changing the `model_size` parameter in the config:
- "tiny": Fastest, least accurate
- "base": Fast, reasonable accuracy
- "small": Good balance of speed and accuracy
- "medium": Better accuracy, slower
- "large": Best accuracy, but slowest and requires more resources