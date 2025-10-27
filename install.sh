#!/bin/bash
# Installation script for HyprSTT

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if running under Hyprland
if [ -z "$HYPRLAND_INSTANCE_SIGNATURE" ]; then
    echo "Warning: HYPRLAND_INSTANCE_SIGNATURE not set. Are you running under Hyprland?"
    echo "Some features may not work correctly."
fi

# Check system dependencies
echo "Checking system dependencies..."
MISSING_DEPS=()

# Mandatory dependencies
for dep in python python3 python-pip socat wtype wl-copy notify-send
do
    if ! command_exists "$dep"; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "Missing required dependencies: ${MISSING_DEPS[*]}"
    echo "Please install them using your package manager."
    echo "For Arch-based distributions:"
    echo "  sudo pacman -S python python-pip portaudio libnotify wtype wl-clipboard socat ffmpeg python-pyqt6 libsndfile"
    echo "For Debian/Ubuntu:"
    echo "  sudo apt-get install python3 python3-pip portaudio19-dev libnotify-bin wtype wl-clipboard socat ffmpeg python3-pyqt6 libsndfile1"
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
if ! command_exists python3; then
    python -m venv venv
else
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create config directory if it doesn't exist
echo "Setting up configuration..."
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/hyprstt"
mkdir -p "$CONFIG_DIR"

# Copy config file if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.yml" ]; then
    cp "config/config.yml" "$CONFIG_DIR/"
    echo "Created configuration file at: $CONFIG_DIR/config.yml"
else
    echo "Configuration file already exists at: $CONFIG_DIR/config.yml"
fi

# Create the trigger script for Hyprland
TRIGGER_SCRIPT="$CONFIG_DIR/trigger.sh"
cat > "$TRIGGER_SCRIPT" << 'EOF'
#!/bin/bash
# This is just a dummy script that will be "executed" when the key combo is pressed
# The application will intercept this event through the Hyprland IPC
exit 0
EOF
chmod +x "$TRIGGER_SCRIPT"
echo "Created trigger script at: $TRIGGER_SCRIPT"

# Suggest Hyprland configuration
echo
echo "Installation complete!"
echo
echo "Please add the following line to your Hyprland configuration file (~/.config/hypr/hyprland.conf):"
echo "bind = SUPER, SPACE, exec, $TRIGGER_SCRIPT"
echo
echo "To start the application manually:"
echo "$ cd $(pwd) && ./run.sh"
echo
echo "To enable autostart with your Hyprland session, add this to your hyprland.conf file:"
echo "exec-once = $(pwd)/run.sh"
echo
echo "For more options, please see the README.md file."
