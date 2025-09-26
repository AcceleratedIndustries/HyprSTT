#!/bin/bash
# Stop script for HyprSTT

# Kill the process if running
if pgrep -f "python -m src.main" > /dev/null; then
    pkill -f "python -m src.main"
    
    # Remove PID file if it exists
    if [ -f ~/.local/share/hyprstt/hyprstt.pid ]; then
        rm ~/.local/share/hyprstt/hyprstt.pid
    fi
    
    notify-send "HyprSTT" "Service stopped."
    echo "HyprSTT stopped."
else
    echo "HyprSTT is not running."
fi