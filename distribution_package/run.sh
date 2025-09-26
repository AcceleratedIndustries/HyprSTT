#!/bin/bash
# Production run script for HyprSTT

# Change to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Create log directory
mkdir -p ~/.local/share/hyprstt/logs

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Make sure we're in the right directory
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# Run the application
nohup python -m src.main > ~/.local/share/hyprstt/logs/hyprstt.log 2>&1 &

# Show notification
notify-send "HyprSTT" "Service started. Use F9 to toggle recording."

# Print PID
echo "HyprSTT started with PID: $!"