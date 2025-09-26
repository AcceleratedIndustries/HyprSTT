#!/bin/bash

# Simple script to toggle STT by sending a signal to the running process
# This can be bound in Hyprland config

# Find the Python process running STT
PID=$(pgrep -f "python -m src.main")

if [ -n "$PID" ]; then
    # Send SIGUSR1 signal to the process
    kill -USR1 $PID
    notify-send "HyprSTT" "Toggle signal sent"
else
    notify-send "HyprSTT" "Process not running"
fi