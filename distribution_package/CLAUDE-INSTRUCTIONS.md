# Instructions for Claude

## Overview

This document contains instructions for Claude or Claude Code to help with understanding and customizing the Hyprland Whisper STT application. When users share this document with Claude, it should provide sufficient context to assist with modifications and troubleshooting.

## Project Description

Hyprland Whisper STT is a speech-to-text application that works with the Hyprland Wayland compositor. The application records audio when triggered by a hotkey, transcribes it using the Whisper model, and copies the transcribed text to the clipboard, displaying a notification to alert the user.

## Key Features

- Speech-to-text transcription using Whisper models
- Hotkey-triggered recording (default: F9)
- Visual recording indicator
- Clipboard-based text output with notifications
- Works on Linux systems with Wayland/Hyprland

## Recent Modifications

The most significant recent changes:

1. **Replaced direct text injection with clipboard approach**:
   - The application now copies transcribed text to the clipboard rather than attempting to type it
   - This resolved issues with garbled text that was occurring with direct typing methods
   - Users now manually paste the text where needed, or applications that auto-detect clipboard changes can use it automatically

2. **Lowered audio level thresholds**:
   - Changed audio level thresholds from 100 to 50 in both audio_capture.py and whisper_processor.py
   - This allows the system to better handle quieter speech

3. **Fixed maximum recording duration**:
   - Changed default max_duration to 0 (unlimited) in config.yml
   - This allows users to record for as long as they need until manually stopping

## Common Customization Requests

Users may ask Claude to help with:

1. Adjusting hotkeys
2. Changing the Whisper model size for better accuracy or speed
3. Modifying audio parameters
4. Customizing visual feedback
5. Adding post-processing to transcribed text
6. Debugging microphone or audio issues
7. Integrating with specific applications

## Key Files and Their Purposes

- `main.py`: Core controller orchestrating all components
- `audio_capture.py`: Handles microphone recording
- `whisper_processor.py`: Processes audio with Whisper model
- `wayland_injector.py`: Handles clipboard operations (despite the name)
- `keyboard_listener.py`: Monitors for hotkey presses
- `visual_indicator.py`: Shows recording status
- `hyprland_manager.py`: Interfaces with Hyprland
- `utils.py`: Utility functions
- `config/config.yml`: Configuration settings
- `requirements.txt`: Python dependencies

## Debugging Information

Common issues and solutions:

1. **Empty transcriptions**:
   - Check audio levels in logs
   - May need to adjust microphone settings or lower thresholds further
   - Check debug audio recordings in ~/.local/share/whisper-stt/debug/

2. **Clipboard not working**:
   - Ensure wl-copy is installed
   - Check logs for clipboard errors
   - May need to modify clipboard approaches based on desktop environment

3. **Hotkey not detected**:
   - Check keyboard listener backend being used
   - May need to use direct Hyprland binding via toggle-stt.sh

## Example Customization Requests

When users share this document with Claude, they may ask for help with modifications like:

1. "Help me change the application to use a different hotkey."
2. "I want to add text formatting to the transcribed output."
3. "Can you help me make the application automatically paste without using the clipboard?"
4. "How can I make the transcription more accurate for my accent?"
5. "Help me add a feature to save transcriptions to a file."

## Instruction for Claude

Claude should:
1. Review the code files mentioned in user queries
2. Understand the system architecture before suggesting changes
3. Provide complete code solutions when modifying files
4. Always suggest testing changes after implementation
5. Guide users on checking logs when troubleshooting
6. Refer to the CUSTOMIZATION.md file for additional information
7. Be cautious about re-enabling direct typing functionality as it may cause issues

When a user asks about customizing features, first examine the relevant code files to understand the current implementation before suggesting changes.