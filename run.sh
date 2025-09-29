#!/bin/bash
# Production run script for HyprSTT

# Change to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Create log directory
mkdir -p ~/.local/share/hyprstt/logs

# Check if already running
if pgrep -f "python -m src.main" > /dev/null; then
    notify-send "HyprSTT" "Already running! Use F9 to toggle recording."
    exit 0
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Make sure we're in the right directory
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# Run the application
nohup python -m src.main > ~/.local/share/hyprstt/logs/hyprstt.log 2>&1 &
APP_PID=$!

# Wait a moment for the app to start
sleep 2

# Check if the application started successfully
if kill -0 $APP_PID 2>/dev/null; then
    notify-send "HyprSTT" "Service started successfully! Use F9 to toggle recording." -t 5000
    echo "HyprSTT started with PID: $APP_PID"
    echo $APP_PID > ~/.local/share/hyprstt/hyprstt.pid
else
    notify-send "HyprSTT" "Failed to start service. Check logs for details." -t 5000
    echo "Failed to start HyprSTT"
    exit 1
fi