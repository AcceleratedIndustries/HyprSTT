# Deployment Guide for Hyprland Whisper STT

This guide provides instructions for distributing and deploying the Hyprland Whisper STT application to your team members.

## Packaging for Distribution

To distribute the application to your team, you can use one of the following methods:

### Method 1: Git Repository

1. Push the updated codebase to a Git repository
2. Share the repository URL with your team members
3. Team members can clone the repository and follow the installation instructions

```bash
# Instructions for team members
git clone https://[your-repo-url]/hyprland-whisper-stt.git
cd hyprland-whisper-stt
./quick-setup.sh
./run.sh
```

### Method 2: Compressed Archive

1. Create a compressed archive of the project directory
2. Share the archive with your team members via file sharing

```bash
# Create the archive
cd /path/to/parent/directory
tar -czvf hyprland-whisper-stt.tar.gz hyprland-whisper-stt

# Instructions for team members
tar -xzvf hyprland-whisper-stt.tar.gz
cd hyprland-whisper-stt
./quick-setup.sh
./run.sh
```

## Required Files

Ensure the following files are included in your distribution:

### Core Files
- All Python source files in `src/`
- Configuration files in `config/`
- Setup and run scripts:
  - `quick-setup.sh`
  - `run.sh`
  - `run-dev.sh`
  - `toggle-stt.sh`
- Requirements file: `requirements.txt`

### Documentation
- `README-UPDATED.md` (rename to `README.md` before distribution)
- `CUSTOMIZATION.md`
- `CLAUDE-INSTRUCTIONS.md`
- `USAGE.md`
- `DEPLOYMENT.md` (this file)

## Team Member Prerequisites

Team members will need:

1. Linux system with Wayland (preferably Hyprland)
2. Python 3.8 or newer
3. Basic system dependencies:
   - `wl-clipboard` package
   - `libnotify` (for `notify-send`)
   - Audio libraries and working microphone
   - (Optional) `xdotool` for alternative input methods

## Installation Verification

After installing, team members should verify installation by:

1. Running the application with `./run-dev.sh`
2. Testing the recording functionality
3. Verifying transcribed text is copied to clipboard
4. Checking for notifications

## System Integration Options

### Service Setup

For team members who want the application to run automatically, provide these instructions:

1. Copy the service file:
   ```bash
   cp hyprland-whisper-stt.service ~/.config/systemd/user/
   ```

2. Enable and start the service:
   ```bash
   systemctl --user enable hyprland-whisper-stt.service
   systemctl --user start hyprland-whisper-stt.service
   ```

### Desktop Integration

For desktop integration:

1. Copy the toggle script to a convenient location:
   ```bash
   mkdir -p ~/.local/bin
   cp toggle-stt.sh ~/.local/bin/
   chmod +x ~/.local/bin/toggle-stt.sh
   ```

2. Add to Hyprland config:
   ```
   # Add to ~/.config/hypr/hyprland.conf
   bind = SUPER, SPACE, exec, ~/.local/bin/toggle-stt.sh
   ```

## Customizing for Team Needs

Each team member can customize their installation:

1. Edit `config/config.yml` for personal preferences
2. For more advanced customizations, refer to `CUSTOMIZATION.md`
3. Use Claude Code with `CLAUDE-INSTRUCTIONS.md` for guidance

## Updating the Application

When you make updates:

1. Increment version number (if applicable)
2. Document changes in a changelog or release notes
3. Distribute using the same method as initial deployment
4. Provide clear upgrade instructions:
   ```bash
   # Pull updates from repository
   git pull
   
   # Or extract updated archive
   tar -xzvf hyprland-whisper-stt-updated.tar.gz
   
   # Restart the application
   ./run.sh
   ```

## Troubleshooting Common Deployment Issues

### Missing Dependencies
If team members report missing dependencies:
```bash
# Install system dependencies
sudo [package-manager] install wl-clipboard libnotify-bin xdotool python3-dev

# Reinstall Python dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

### Audio Device Issues
If microphone is not detected:
```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 test.wav && aplay test.wav
```

### Permissions Issues
For audio or notification issues:
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
```

## Support Resources

Provide team members with:

1. Contact information for the technical point of contact
2. Link to the application documentation
3. Instructions on how to gather logs for troubleshooting:
   ```bash
   # Collect logs
   cat ~/.local/share/whisper-stt/logs/whisper_stt.log
   ```

## Further Customization with Claude

Remind team members to use Claude Code with the provided `CLAUDE-INSTRUCTIONS.md` file to get assistance with customization and troubleshooting.