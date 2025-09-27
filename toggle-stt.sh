#!/bin/bash

# HyprSTT Toggle Script
# Sends toggle signal to running HyprSTT process
# Can be bound to any hotkey in Wayland compositors (Hyprland, Niri, Sway, etc.)

set -euo pipefail

# Configuration
PROCESS_NAME="python -m src.main"
STATE_FILE="$HOME/.local/share/hyprstt/state"
NOTIFICATION_TIMEOUT=2

# Ensure state directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Find the Python process running STT
PIDS=$(pgrep -f "$PROCESS_NAME" || true)

if [ -z "$PIDS" ]; then
    notify-send "HyprSTT" "Process not running - start HyprSTT first" --expire-time=${NOTIFICATION_TIMEOUT}000
    exit 1
fi

# Handle multiple instances
PID_COUNT=$(echo "$PIDS" | wc -l)
if [ "$PID_COUNT" -gt 1 ]; then
    notify-send "HyprSTT" "Warning: Multiple instances detected, using first one" --expire-time=${NOTIFICATION_TIMEOUT}000
fi

# Use the first PID
PID=$(echo "$PIDS" | head -n1)

# Send SIGUSR1 signal to toggle recording
if kill -USR1 "$PID" 2>/dev/null; then
    # Try to determine current state for better notification
    if [ -f "$STATE_FILE" ]; then
        STATE=$(cat "$STATE_FILE" 2>/dev/null || echo "unknown")
        case "$STATE" in
            "recording")
                notify-send "HyprSTT" "🎤 Recording started" --expire-time=${NOTIFICATION_TIMEOUT}000
                ;;
            "idle")
                notify-send "HyprSTT" "⏹️ Recording stopped" --expire-time=${NOTIFICATION_TIMEOUT}000
                ;;
            *)
                notify-send "HyprSTT" "🔄 Recording toggled" --expire-time=${NOTIFICATION_TIMEOUT}000
                ;;
        esac
    else
        notify-send "HyprSTT" "🔄 Recording toggled" --expire-time=${NOTIFICATION_TIMEOUT}000
    fi
else
    notify-send "HyprSTT" "❌ Failed to send toggle signal" --expire-time=${NOTIFICATION_TIMEOUT}000
    exit 1
fi