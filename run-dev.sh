#!/bin/bash
# Development run script for HyprSTT

# Change to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Create necessary directories
mkdir -p ~/.local/share/hyprstt

# Check if already running
if pgrep -f "python -m src.main" > /dev/null; then
    echo "HyprSTT is already running! Use F9 to toggle recording."
    exit 0
fi

# Determine which Python to use
if [ -d "venv" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
elif [ -d ".venv" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
else
    PYTHON_CMD="python"
fi

# Make sure we're in the right directory
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# Run the application in debug mode in background so we can capture PID
"$PYTHON_CMD" -m src.main &
APP_PID=$!

# Save PID for toggle script
echo $APP_PID > ~/.local/share/hyprstt/hyprstt.pid

# Wait for the background process to complete
wait $APP_PID

# Clean up PID file when process exits
rm -f ~/.local/share/hyprstt/hyprstt.pid