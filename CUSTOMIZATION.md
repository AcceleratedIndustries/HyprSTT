# Hyprland Whisper STT - Customization Guide

This document provides guidance on how to customize the Hyprland Whisper STT application using Claude Code. By providing this document's content to Claude Code, your team members can easily understand and modify the application to fit their specific needs.

## Using Claude Code for Customization

[Claude Code](https://claude.ai/code) is an interactive CLI tool that can help you understand and modify the codebase. To use Claude Code effectively for customizing this application:

1. Clone the repository to your local machine
2. Open Claude Code in the repository directory
3. Share this document with Claude Code to provide context about the application

Example command to start Claude Code:
```bash
cd hyprland-whisper-stt
claude code
```

## Project Overview

Hyprland Whisper STT is a speech-to-text application designed to work with the Hyprland Wayland compositor. The application:

1. Listens for a hotkey (default: F9)
2. Records audio while the hotkey is held or until toggled off
3. Transcribes the audio using the Whisper speech recognition model
4. Copies the transcribed text to the clipboard
5. Shows a notification with the transcribed text

The application is now configured to use a clipboard-based approach rather than direct text injection, which provides better reliability and user control.

## Key Components

The application consists of several Python modules, each handling specific functionality:

- `main.py`: The core controller that orchestrates all components
- `audio_capture.py`: Handles recording audio from the microphone
- `whisper_processor.py`: Processes audio and generates transcriptions
- `wayland_injector.py`: Handles copying text to clipboard (renamed but still handles text output)
- `keyboard_listener.py`: Monitors keyboard for hotkey presses
- `visual_indicator.py`: Shows a visual indicator when recording
- `hyprland_manager.py`: Interfaces with Hyprland
- `utils.py`: Contains utility functions

## Common Customizations

Here are some common customizations your team might want to make:

### 1. Changing the Hotkey

To change the hotkey combination:

1. Edit `config/config.yml`
2. Modify the `hotkeys` section:
   ```yaml
   hotkeys:
     toggle_recording: ["F9"]  # Change to your preferred key
     use_hypr_dispatch: false
   ```

### 2. Adjusting Audio Parameters

For better audio capture quality or to adjust recording behavior:

1. Edit `config/config.yml`
2. Modify the `audio` section:
   ```yaml
   audio:
     rate: 16000  # Sample rate (Hz)
     chunk: 4096  # Buffer size
     channels: 1  # Mono audio
     max_duration: 0  # Maximum recording duration (0 for unlimited)
   ```

### 3. Changing Whisper Model Size

To balance transcription accuracy and speed:

1. Edit `config/config.yml`
2. Modify the `whisper` section:
   ```yaml
   whisper:
     model_size: "medium"  # Options: tiny, base, small, medium, large
     device: "auto"  # Options: cpu, cuda, auto
     compute_type: "float32"  # Options: float16, float32, int8
   ```

### 4. Customizing Visual Feedback

To adjust the visual indicators, notifications, and tray icon menu:

1. Edit `config/config.yml` (or `~/.config/hyprstt/config.yml` for existing installations)
2. Modify the `ui` section:
   ```yaml
   ui:
     notifications: true
     notification_timeout: 2
     tray_icon: true  # Enable system tray icon
     tray_menu_font_size: 11  # Font size for tray icon menu (default: 11)
     visual_indicator:
       enabled: true
       type: "overlay"
       position: "top-right"
       size: "medium"
       color: "#ff0000"
       opacity: 0.8
       pulse: true
   ```

**Note for existing users**: If you're upgrading from a previous version, add the `tray_menu_font_size: 11` line to your `~/.config/hyprstt/config.yml` file under the `ui` section to customize the tray menu font size.

### 5. Modifying Notification Behavior

If you want to change how notifications work:

1. Locate the relevant code in `main.py` around line 400
2. Modify the notification creation code

### 6. Adjusting Audio Level Thresholds

For better handling of quiet audio:

1. Edit `src/whisper_processor.py`
2. Look for the audio level threshold checks (around line 136)
3. Adjust the threshold values (e.g., from 50 to a lower value if needed)

### 7. Adding Custom Post-Processing to Transcriptions

To filter or modify transcribed text before copying to clipboard:

1. Edit `src/whisper_processor.py`
2. Look for the section after transcription (around line 200)
3. Add your custom filtering or processing code before returning the result

### 8. Enable Automatic Typing (NOT RECOMMENDED)

The current application uses clipboard-only mode for reliability. However, if you want to re-enable automatic typing (with caution):

1. Edit `src/wayland_injector.py`
2. Look for the disabled keyboard injection methods
3. Uncomment and restore the original functionality (refer to git history)

## Installation for Team Members

Team members can install the application using:

```bash
# Clone the repository
git clone https://[your-repo-url]/hyprland-whisper-stt.git
cd hyprland-whisper-stt

# Run the quick setup script
./quick-setup.sh

# Start the application
./run-dev.sh
```

## Troubleshooting Tips

When using Claude Code to help with troubleshooting:

1. Ask Claude to examine log files: `~/.local/share/whisper-stt/logs/whisper_stt.log`
2. Check debug audio files for failed transcriptions: `~/.local/share/whisper-stt/debug/`
3. Use Claude to suggest fixes for specific issues (e.g., "The application is not detecting my microphone")

## Recent Fixes

The application has recently been updated to:

1. Lower audio silence thresholds for better detection of quiet speech
2. Switch from direct keyboard injection to clipboard-based approach
3. Improve error handling and debugging information
4. Fix issues with maximum recording duration

## Getting Help

If you encounter issues while customizing:

1. Use Claude Code to examine the relevant code files
2. Check the application logs in `~/.local/share/whisper-stt/logs/`
3. Refer to the original documentation in the repository
4. Reach out to the team lead for assistance