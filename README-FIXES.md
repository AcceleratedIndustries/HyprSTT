# This document provides a guide for setting up and running the Hyprland Whisper Speech-to-Text system.

## Quick Setup

1. **Create and activate a virtual environment:**

   ```bash
   cd /home/will/claude-stt/hyprland-whisper-stt
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install required packages:**

   ```bash
   pip install --upgrade pip
   pip install pyaudio numpy torch torchaudio faster-whisper PyYAML pynput sounddevice soundfile
   ```

3. **Run the application:**

   ```bash
   ./run-dev.sh
   ```

## Usage

1. When the application is running, press **Super+Space** to start recording audio
2. Speak clearly into your microphone
3. Press **Super+Space** again to stop recording and process the speech
4. The transcribed text will be injected into the currently focused window/input field

## Changes Made to Fix Issues

1. **Fixed Whisper model initialization:**
   - Changed compute type from float16 to float32
   - Added proper error handling for model loading
   - Improved path handling for model cache

2. **Enhanced Hyprland integration:**
   - Added fallback mechanisms for finding Hyprland sockets
   - Improved error handling for Hyprland IPC
   - Implemented robust window detection

3. **Added better keyboard listener:**
   - Implemented a multi-backend keyboard listener
   - Added pynput support which doesn't require root access
   - Maintained evdev support as a fallback

4. **Added better error handling:**
   - Improved logging with detailed error messages
   - Added graceful fallbacks for all components
   - Ensured clear user feedback

## Troubleshooting

### Missing Dependencies

If you encounter "No module named X" errors, install the missing package:

```bash
pip install <package-name>
```

### Permission Issues

If you have permission issues with audio or keyboard access:

1. For audio: `sudo usermod -a -G audio $USER`
2. For keyboard: The pynput backend should work without special permissions

### Hyprland Socket Error

If you see "No such file or directory" errors with Hyprland socket:

1. Make sure you're running Hyprland
2. The app will automatically fall back to direct keyboard monitoring

### Audio Input Issues

If audio recording doesn't work:

1. Check your microphone with: `arecord -l`
2. Test recording with: `arecord -d 5 test.wav && aplay test.wav`

## Log Location

Log files are stored at: `~/.local/share/whisper-stt/logs/whisper_stt.log`
