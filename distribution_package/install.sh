#!/bin/bash
# Installation script for HyprSTT

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Detect compositor
COMPOSITOR="unknown"
if [ -n "$HYPRLAND_INSTANCE_SIGNATURE" ]; then
    COMPOSITOR="hyprland"
elif pgrep -x niri > /dev/null; then
    COMPOSITOR="niri"
elif [ -n "$SWAYSOCK" ]; then
    COMPOSITOR="sway"
elif pgrep -x kwin_wayland > /dev/null; then
    COMPOSITOR="kwin"
fi

echo "Detected compositor: $COMPOSITOR"

# Check system dependencies
echo "Checking system dependencies..."
MISSING_DEPS=()

# Mandatory dependencies
for dep in python python3 pip socat wtype
do
    if ! command_exists "$dep"; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "Missing required dependencies: ${MISSING_DEPS[*]}"
    echo "Please install them using your package manager."
    echo "For Arch-based distributions:"
    echo "  sudo pacman -S ${MISSING_DEPS[*]}"
    echo "For Debian/Ubuntu:"
    echo "  sudo apt-get install ${MISSING_DEPS[*]}"
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

# Install desktop entry for application launchers
echo "Installing desktop entry..."
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

# Update desktop entry with correct paths
sed "s|SCRIPT_DIR|$(pwd)|g" hyprstt.desktop > "$DESKTOP_DIR/hyprstt.desktop"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || echo "Desktop database update skipped (update-desktop-database not found)"
echo "Installed desktop entry at: $DESKTOP_DIR/hyprstt.desktop"

# Create the trigger script for Hyprland compatibility
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
echo "The application is now available in your application launcher as 'HyprSTT'."
echo

case "$COMPOSITOR" in
    "hyprland")
        echo "=== Hyprland Setup ==="
        echo "Add this line to your Hyprland configuration file (~/.config/hypr/hyprland.conf):"
        echo "bind = SUPER, SPACE, exec, $TRIGGER_SCRIPT"
        echo
        echo "For autostart, add:"
        echo "exec-once = $(pwd)/run.sh"
        ;;
    "niri")
        echo "=== Niri Setup ==="
        echo "Add this line to your Niri configuration file (~/.config/niri/config.kdl):"
        echo "    F9 hotkey-overlay-title=\"Toggle Speech-to-Text Recording\" { spawn \"$(pwd)/toggle-stt.sh\"; }"
        echo
        echo "For autostart, add:"
        echo "spawn-at-startup \"$(pwd)/run-niri.sh\""
        ;;
    "sway")
        echo "=== Sway Setup ==="
        echo "Add this line to your Sway configuration file (~/.config/sway/config):"
        echo "bindsym F9 exec $(pwd)/toggle-stt.sh"
        echo
        echo "For autostart, add:"
        echo "exec $(pwd)/run.sh"
        ;;
    *)
        echo "=== Generic Wayland Setup ==="
        echo "Use your compositor's keybind configuration to bind F9 to:"
        echo "$(pwd)/toggle-stt.sh"
        echo
        echo "For manual start:"
        echo "$ cd $(pwd) && ./run-niri.sh"
        ;;
esac

echo
echo "For more options, please see the README.md file."