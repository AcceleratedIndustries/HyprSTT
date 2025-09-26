# Hyprland Whisper STT Distribution Package

This package contains the updated Hyprland Whisper STT application with the clipboard-based text output system. This README explains the contents of this package and how to deploy it to your team.

## Package Contents

### Core Application Files
- `src/`: Python source code for the application
- `config/`: Configuration files
- `*.sh`: Script files for setup and running
- `requirements.txt`: Python dependencies
- `hyprland-whisper-stt.service`: Systemd service file

### Documentation Files
- `README-UPDATED.md`: Updated main README for the application (rename to README.md before distribution)
- `CUSTOMIZATION.md`: Guide for customizing the application
- `CLAUDE-INSTRUCTIONS.md`: Instructions for using Claude/Claude Code with this application
- `USAGE.md`: Usage guide for end users
- `DEPLOYMENT.md`: Guide for deploying to team members
- `PACKAGE-README.md`: This file

## Changes Since Last Version

The application has been updated to:

1. **Replace direct text injection with clipboard approach**:
   - Transcribed text is now copied to clipboard instead of being typed
   - This fixes the issue with garbled text that occurred with direct typing
   - Users now manually paste the text where needed

2. **Lower audio level thresholds**:
   - Changed threshold from 100 to 50 to better handle quieter speech
   - Improved detection of speech in quieter environments

3. **Fix maximum recording duration**:
   - Changed default max_duration to 0 (unlimited)
   - Recording now continues until manually stopped

## Deployment Instructions

See `DEPLOYMENT.md` for detailed deployment instructions.

Quick steps:
1. Choose a distribution method (Git repo or compressed archive)
2. Include all files in this package
3. Share with team members
4. Team members install following the quick-setup instructions

## Team Instructions

Team members should:
1. Install the application using `./quick-setup.sh`
2. Run the application with `./run.sh`
3. Configure the application by editing `config/config.yml`
4. Refer to `USAGE.md` for usage instructions
5. Use `CUSTOMIZATION.md` and `CLAUDE-INSTRUCTIONS.md` for customization help

## Using Claude Code for Customization

The `CLAUDE-INSTRUCTIONS.md` file is designed to be shared with Claude Code to provide context about the application. Team members can:

1. Open Claude Code in the application directory
2. Share the Claude instructions document with Claude
3. Ask for help with specific customization tasks

## Support

For team members needing support:
1. Check the documentation files for troubleshooting guidance
2. Examine logs in `~/.local/share/whisper-stt/logs/`
3. Use Claude Code with the provided instruction document
4. Contact team lead for further assistance