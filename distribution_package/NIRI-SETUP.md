# Niri Setup Guide for Whisper STT

This guide explains how to set up Whisper STT specifically for the Niri Wayland compositor.

## Quick Setup

1. **Run the installer**: `./install.sh` (automatically detects Niri)
2. **Launch from application menu**: Search for "Whisper STT" in fuzzel/rofi
3. **Use F9 to toggle recording** (if you added the keybind)

## Niri Configuration

### Adding Hotkey (Recommended)

Add this line to your `~/.config/niri/config.kdl` in the `binds` section:

```kdl
F9 hotkey-overlay-title="Toggle Speech-to-Text Recording" { spawn "/path/to/whisper-stt/toggle-stt.sh"; }
```

### Autostart (Optional)

Add this line to your `~/.config/niri/config.kdl`:

```kdl
spawn-at-startup "/path/to/whisper-stt/run-niri.sh"
```

## Notification Setup

Whisper STT requires a notification daemon for user feedback. For Niri, we recommend **mako**:

### Install Mako
```bash
# Arch/Manjaro
sudo pacman -S mako

# Ubuntu/Debian  
sudo apt install mako-notifier
```

### Configure Mako
Create `~/.config/mako/config`:
```ini
anchor=top-right
font=monospace 10
background-color=#2e3440
text-color=#d8dee9
width=300
height=100
border-size=2
border-color=#5e81ac
border-radius=10
default-timeout=5000
```

### Start Mako
Add to your `~/.config/niri/config.kdl`:
```kdl
spawn-at-startup "mako"
```

## Usage

1. **Start the service**: Launch "Whisper STT" from your application launcher
2. **Toggle recording**: Press F9 (or run `./toggle-stt.sh`)
3. **Get transcription**: Text is automatically copied to clipboard
4. **Stop service**: Run `./stop.sh`

## Troubleshooting

### F9 Key Not Working
If F9 doesn't work, the issue is likely keyboard permissions. Use the toggle script instead:
```bash
./toggle-stt.sh
```

### No Notifications
Make sure mako is running:
```bash
# Check if mako is running
pgrep mako

# Start mako manually
mako &

# Or restart it
pkill mako && mako &
```

### Service Won't Start
Check the logs:
```bash
tail -f ~/.local/share/whisper-stt/logs/whisper-stt.log
```

### Audio Issues
Test your microphone:
```bash
# Test recording
arecord -d 3 test.wav && aplay test.wav

# Check audio devices
python -c "from src.utils import get_audio_devices; print(get_audio_devices())"
```

## Advanced Configuration

### Custom Hotkey
You can bind the toggle script to any key combination in Niri:
```kdl
Mod+Shift+M { spawn "/path/to/whisper-stt/toggle-stt.sh"; }
```

### Different Whisper Model
Edit `~/.config/whisper-stt/config.yml`:
```yaml
whisper:
  model_size: "small"  # tiny, base, small, medium, large
```

### Visual Indicator
The visual indicator shows recording status in the top-right corner. Configure in `config.yml`:
```yaml
ui:
  visual_indicator:
    enabled: true
    position: "top-right"
    color: "#ff0000"
```

## Files Reference

- **Desktop entry**: `~/.local/share/applications/hyprland-whisper-stt.desktop`
- **Configuration**: `~/.config/whisper-stt/config.yml`
- **Logs**: `~/.local/share/whisper-stt/logs/whisper-stt.log`
- **Failed audio**: `~/.local/share/whisper-stt/debug/`