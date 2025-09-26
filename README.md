# Hyprland Whisper STT

A Speech-to-Text system for Hyprland and Wayland environments using OpenAI's Whisper for speech recognition.

## Features

- Records audio from your microphone when triggered by a keyboard shortcut
- Processes speech using Whisper's speech recognition (runs locally on your machine)
- Injects transcribed text into the currently focused window/input field
- Works with terminals, text editors, browsers, and other applications
- Built specifically for Hyprland/Wayland compatibility
- Customizable through configuration file

## Requirements

### System Requirements

- Linux distribution with Hyprland/Wayland compositor
- Python 3.8 or higher
- Working microphone
- Wayland-compatible input tools (wtype or ydotool)

### Required System Packages

Install the following packages using your distribution's package manager:

```bash
# For Arch-based distributions (including those using Hyprland)
sudo pacman -S python python-pip portaudio libnotify wtype socat ffmpeg

# For Ubuntu/Debian-based with Wayland
sudo apt-get update
sudo apt-get install -y \
  python3-pip \
  python3-dev \
  portaudio19-dev \
  libnotify-bin \
  socat \
  libpulse-dev \
  ffmpeg

# Install wtype (Wayland typing tool)
# For Arch:
sudo pacman -S wtype

# For other distributions you may need to compile from source:
git clone https://github.com/atx/wtype.git
cd wtype
meson build
ninja -C build
sudo ninja -C build install
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hyprland-whisper-stt.git
cd hyprland-whisper-stt
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuration

The default configuration file is located at `~/.config/whisper-stt/config.yml`. You can create it with these commands:

```bash
mkdir -p ~/.config/whisper-stt
cp config/config.yml ~/.config/whisper-stt/
```

Edit the configuration file according to your preferences:

```yaml
audio:
  rate: 16000  # Sample rate (Hz)
  chunk: 1024  # Buffer size
  channels: 1  # Mono audio

whisper:
  model_size: "small"  # Options: tiny, base, small, medium, large
  device: "auto"  # Options: cpu, cuda, auto
  compute_type: "float16"  # Options: float16, float32, int8
  language: "en"  # Language code (leave empty for auto-detect)
  models_dir: "~/.cache/whisper"  # Directory to store models

hotkeys:
  toggle_recording: ["SUPER", "SPACE"]  # Hotkey combination
  use_hypr_dispatch: true  # Use Hyprland IPC for hotkey detection

ui:
  notifications: true  # Enable desktop notifications
  notification_timeout: 2  # Notification display time in seconds
```

### 5. Configuring Hyprland

Option 1: Using Hyprland's own binds (recommended):

Edit your Hyprland configuration file (usually at `~/.config/hypr/hyprland.conf`) and add:

```Hyprland
# Define a bind that will be captured by our application
bind = SUPER, SPACE, exec, ~/.config/whisper-stt/trigger.sh
```

Create the trigger script at `~/.config/whisper-stt/trigger.sh`:

```bash
#!/bin/bash
# This is just a dummy script that will be "executed" when the key combo is pressed
# Our application will intercept this event through the Hyprland IPC
exit 0
```

Make the script executable:

```bash
chmod +x ~/.config/whisper-stt/trigger.sh
```

Option 2: Using direct keyboard monitoring:

Edit your configuration file at `~/.config/whisper-stt/config.yml`:

```yaml
hotkeys:
  toggle_recording: ["SUPER", "SPACE"]  # Hotkey combination
  use_hypr_dispatch: false  # Use direct keyboard monitoring instead
```

Add your user to the `input` group:

```bash
sudo usermod -a -G input $USER
```

Then log out and log back in for the changes to take effect.

## Usage

### Running Manually

```bash
# From the project directory
source venv/bin/activate  # If using virtual environment
python -m src.main
```

### Starting Automatically with Hyprland

To start the application automatically when Hyprland starts, add to your Hyprland configuration file (`~/.config/hypr/hyprland.conf`):

```Hyprland
exec-once = /path/to/hyprland-whisper-stt/run.sh
```

Create the startup script (`run.sh`):

```bash
#!/bin/bash
# File: /path/to/hyprland-whisper-stt/run.sh

cd /path/to/hyprland-whisper-stt
source venv/bin/activate
python -m src.main
```

Make the script executable:

```bash
chmod +x /path/to/hyprland-whisper-stt/run.sh
```

### Using the STT System

1. Start the application
2. Press the configured hotkey (default: Super+Space) to start recording
3. Speak clearly into your microphone
4. Press the hotkey again to stop recording and process speech
5. The transcribed text will be typed into the currently focused window/input field

## Troubleshooting

### Audio Issues

If the application can't access your microphone:

1. Check if your microphone is working:

   ```bash
   arecord -l  # List recording devices
   ```

2. Test recording:

   ```bash
   arecord -d 5 test.wav  # Record 5 seconds
   aplay test.wav  # Play recording
   ```

3. Ensure your user has audio permissions:

   ```bash
   sudo usermod -a -G audio $USER
   ```

### Application Not Starting

1. Check the logs:

   ```bash
   cat ~/.local/share/whisper-stt/logs/whisper_stt.log
   ```

2. Verify dependencies:

   ```bash
   python -c "from src.utils import check_dependencies; check_dependencies()"
   ```

3. Test PyTorch installation:

   ```bash
   python -c "import torch; print(torch.__version__)"
   python -c "import torch; print(torch.cuda.is_available())"
   ```

### Text Injection Issues

If text is not being injected into applications:

1. Check if `wtype` is installed:

   ```bash
   which wtype
   ```

2. Test text injection manually:

   ```bash
   wtype "test text"
   ```

3. Ensure Wayland environment variables are set correctly:

   ```bash
   echo $WAYLAND_DISPLAY
   echo $XDG_SESSION_TYPE  # Should be "wayland"
   ```

### Hyprland IPC Issues

If the application can't connect to Hyprland:

1. Check if the Hyprland socket exists:

   ```bash
   echo $HYPRLAND_INSTANCE_SIGNATURE
   ls -la /tmp/hypr/$(echo $HYPRLAND_INSTANCE_SIGNATURE)/.socket.sock
   ```

2. Test Hyprland IPC manually:

   ```bash
   echo '["workspaces"]' | socat - UNIX-CONNECT:/tmp/hypr/$(echo $HYPRLAND_INSTANCE_SIGNATURE)/.socket.sock
   ```

## Performance Optimization

- For faster transcription:
  - Use a smaller model (`tiny` or `base`)
  - Enable GPU acceleration if available
  - Set `compute_type` to `int8` for faster processing but slightly lower accuracy

- For better accuracy:
  - Use a larger model (`medium` or `large`)
  - Set `compute_type` to `float32`
  - Set the appropriate language in the configuration

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.

For third-party dependencies and their licenses, see [LICENSES.md](LICENSES.md).
