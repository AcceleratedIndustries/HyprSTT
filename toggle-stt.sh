#!/bin/bash

# HyprSTT Toggle Script
# Sends toggle signal to running HyprSTT process
# Can be bound to any hotkey in Wayland compositors (Hyprland, Niri, Sway, etc.)

set -euo pipefail

# Configuration
PROCESS_PATTERNS=(
    "python -m src.main"           # Standard mode
    "python -m src.tui_controller" # TUI mode
    "hyprstt-tui"                  # TUI launcher script
)
STATE_FILE="$HOME/.local/share/hyprstt/state"
NOTIFICATION_TIMEOUT=2
DEBUG_LOG="$HOME/.local/share/hyprstt/toggle-debug.log"

# Ensure state directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Try to get PID from file first, then fall back to pgrep
PID_FILE="$HOME/.local/share/hyprstt/hyprstt.pid"
PID=""

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
    # Validate that the PID is still running and is the correct process
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        # Check if it's actually our process - check for either standard or TUI mode
        CMD_LINE=$(ps -p "$PID" -o cmd= 2>/dev/null || echo "")
        if [ -n "$CMD_LINE" ] && (echo "$CMD_LINE" | grep -q "src\.main" || echo "$CMD_LINE" | grep -q "src\.tui_controller" || echo "$CMD_LINE" | grep -q "hyprstt-tui"); then
            # PID is valid and correct process
            echo "$(date): DEBUG: Using PID from file: $PID" >> "$DEBUG_LOG"
        else
            echo "$(date): DEBUG: PID file exists but process doesn't match. CMD: $CMD_LINE" >> "$DEBUG_LOG"
            PID=""
        fi
    else
        echo "$(date): DEBUG: PID from file not running or kill -0 failed" >> "$DEBUG_LOG"
        PID=""
    fi
fi

# Fall back to pgrep if PID file method failed
if [ -z "$PID" ]; then
    echo "$(date): DEBUG: Falling back to pgrep" >> "$DEBUG_LOG"

    # Try each process pattern until we find one
    for PROCESS_NAME in "${PROCESS_PATTERNS[@]}"; do
        PIDS=$(pgrep -f "$PROCESS_NAME" || true)
        if [ -n "$PIDS" ]; then
            echo "$(date): DEBUG: Found process using pattern: $PROCESS_NAME" >> "$DEBUG_LOG"
            break
        fi
    done

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
fi

# Send SIGUSR1 signal to toggle recording
echo "$(date): DEBUG: About to send SIGUSR1 to PID: $PID" >> "$DEBUG_LOG"
echo "$(date): DEBUG: Process info: $(ps -p "$PID" -o pid,ppid,cmd 2>/dev/null || echo 'Process not found')" >> "$DEBUG_LOG"
echo "$(date): DEBUG: Current focused window PID: $(hyprctl activewindow | grep -E 'pid:' | cut -d' ' -f2 2>/dev/null || echo 'unknown')" >> "$DEBUG_LOG"

if kill -USR1 "$PID" 2>/dev/null; then
    echo "$(date): DEBUG: Successfully sent SIGUSR1 to PID $PID" >> "$DEBUG_LOG"
    # Python process will handle notifications based on actual state changes
    # No notification here to avoid race condition with state file
else
    notify-send "HyprSTT" "❌ Failed to send toggle signal" --expire-time=${NOTIFICATION_TIMEOUT}000
    exit 1
fi