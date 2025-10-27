#!/bin/bash
# Quick setup script for HyprSTT

# Detect package manager
if command -v pacman &> /dev/null; then
    echo "Arch-based system detected."
    echo "Installing system dependencies..."
    echo "You may be prompted for sudo password to install system packages."
    sudo pacman -S --needed python python-pip python-virtualenv portaudio libnotify wtype wl-clipboard socat ffmpeg python-pyqt6 libsndfile
elif command -v apt-get &> /dev/null; then
    echo "Debian/Ubuntu-based system detected."
    echo "Installing system dependencies..."
    echo "You may be prompted for sudo password to install system packages."
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv python3-dev portaudio19-dev libnotify-bin wtype wl-clipboard socat libpulse-dev ffmpeg python3-pyqt6 libsndfile1
else
    echo "Unknown package manager. Please install the following dependencies manually:"
    echo "- Python 3.8+ with pip and venv"
    echo "- PortAudio development libraries"
    echo "- libnotify"
    echo "- wtype (for text injection)"
    echo "- wl-clipboard (wl-copy for clipboard operations)"
    echo "- socat (for Hyprland IPC)"
    echo "- ffmpeg (for audio processing)"
    echo "- Qt6/PyQt6 libraries"
    echo "- libsndfile (for soundfile)"
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create config directory
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/hyprstt"
mkdir -p "$CONFIG_DIR"

# Copy config file
if [ ! -f "$CONFIG_DIR/config.yml" ]; then
    cp "config/config.yml" "$CONFIG_DIR/"
    echo "Created configuration file at: $CONFIG_DIR/config.yml"
else
    echo "Configuration file already exists at: $CONFIG_DIR/config.yml"
fi

echo "Setup complete! You can now run the application with:"
echo "./run-dev.sh"