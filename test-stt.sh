#!/bin/bash
# HyprSTT Functionality Test Script
# Tests the basic STT recording and toggle functionality

set -euo pipefail

echo "=========================================="
echo "HyprSTT Functionality Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROCESS_NAME="python -m src.main"
TEST_PASSED=true

# Function to print colored status
print_status() {
    if [ "$1" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    elif [ "$1" = "FAIL" ]; then
        echo -e "${RED}✗ FAIL${NC}: $2"
        TEST_PASSED=false
    elif [ "$1" = "INFO" ]; then
        echo -e "${YELLOW}ℹ INFO${NC}: $2"
    fi
}

# Test 1: Check if HyprSTT is running
echo "Test 1: Check if HyprSTT is running"
PID=$(pgrep -f "$PROCESS_NAME" | head -n1 || echo "")
if [ -n "$PID" ]; then
    print_status "PASS" "HyprSTT is running (PID: $PID)"
else
    print_status "FAIL" "HyprSTT is not running"
    echo ""
    echo "To start HyprSTT, run: ./run-dev.sh"
    exit 1
fi
echo ""

# Test 2: Check if toggle script exists and is executable
echo "Test 2: Check toggle script"
if [ -x "./toggle-stt.sh" ]; then
    print_status "PASS" "Toggle script exists and is executable"
else
    print_status "FAIL" "Toggle script not found or not executable"
fi
echo ""

# Test 3: Test recording toggle (start)
echo "Test 3: Start recording"
print_status "INFO" "Sending toggle signal to start recording..."
if ./toggle-stt.sh; then
    sleep 1
    # Check state file
    if [ -f "$HOME/.local/share/hyprstt/state" ]; then
        STATE=$(cat "$HOME/.local/share/hyprstt/state")
        if [ "$STATE" = "recording" ]; then
            print_status "PASS" "Recording started successfully (state: $STATE)"
        else
            print_status "FAIL" "Recording did not start (state: $STATE)"
        fi
    else
        print_status "FAIL" "State file not found"
    fi
else
    print_status "FAIL" "Toggle script failed"
fi
echo ""

# Test 4: Wait for recording
echo "Test 4: Record test audio"
print_status "INFO" "Recording for 3 seconds - please speak now!"
print_status "INFO" "Say something like: 'This is a test of HyprSTT functionality'"
sleep 3
echo ""

# Test 5: Stop recording and transcribe
echo "Test 5: Stop recording and transcribe"
print_status "INFO" "Sending toggle signal to stop recording..."
if ./toggle-stt.sh; then
    sleep 2
    # Check state file
    if [ -f "$HOME/.local/share/hyprstt/state" ]; then
        STATE=$(cat "$HOME/.local/share/hyprstt/state")
        if [ "$STATE" = "idle" ]; then
            print_status "PASS" "Recording stopped successfully (state: $STATE)"
        else
            print_status "FAIL" "Recording did not stop (state: $STATE)"
        fi
    else
        print_status "FAIL" "State file not found"
    fi
else
    print_status "FAIL" "Toggle script failed"
fi
echo ""

# Test 6: Check clipboard for transcribed text
echo "Test 6: Check clipboard for transcribed text"
sleep 2  # Give transcription time to complete
if command -v wl-paste &> /dev/null; then
    CLIPBOARD_CONTENT=$(wl-paste 2>/dev/null || echo "")
    if [ -n "$CLIPBOARD_CONTENT" ] && [ "$CLIPBOARD_CONTENT" != " " ]; then
        print_status "PASS" "Transcribed text found in clipboard"
        echo ""
        echo "Transcribed text:"
        echo "----------------"
        echo "$CLIPBOARD_CONTENT"
        echo "----------------"
    else
        print_status "FAIL" "No transcribed text in clipboard (may have been silence)"
        print_status "INFO" "Check ~/.local/share/hyprstt/logs/hyprstt.log for details"
    fi
else
    print_status "FAIL" "wl-paste not available (wl-clipboard not installed)"
fi
echo ""

# Test 7: Check for errors in recent logs
echo "Test 7: Check for errors in logs"
LOG_FILE="$HOME/.local/share/hyprstt/logs/hyprstt.log"
if [ -f "$LOG_FILE" ]; then
    ERROR_COUNT=$(tail -n 50 "$LOG_FILE" | grep -c "ERROR" || echo "0")
    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_status "PASS" "No errors in recent logs"
    else
        print_status "FAIL" "Found $ERROR_COUNT error(s) in recent logs"
        print_status "INFO" "Check $LOG_FILE for details"
    fi
else
    print_status "INFO" "Log file not found (running in dev mode?)"
fi
echo ""

# Summary
echo "=========================================="
if $TEST_PASSED; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    echo "Check the output above for details"
    exit 1
fi
