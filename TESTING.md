# HyprSTT Testing Guide

This document describes how to test HyprSTT functionality to ensure the Speech-to-Text system is working correctly after changes.

## Why Test STT Functionality?

After making changes to HyprSTT, it's important to verify that the core functionality still works:
- Recording can be started and stopped
- Audio is captured properly
- Transcription completes successfully
- Text is copied to clipboard

Previous issues we've encountered:
- **Signal handling blocked by Qt event loop**: Python signal handlers weren't being processed because Qt's event loop took over
- **Inverted notifications**: Toggle script showed wrong state due to race condition with state file
- **Multiple running instances**: Caused confusion about which process was receiving signals

## Automated Testing

### Quick Test Script

Run the automated test script:

```bash
cd hyprstt
./test-stt.sh
```

This will:
1. Check if HyprSTT is running
2. Verify toggle script is functional
3. Start recording
4. Wait 3 seconds (speak during this time!)
5. Stop recording
6. Check clipboard for transcribed text
7. Verify no errors in logs

**Expected output:**
```
✓ PASS: HyprSTT is running
✓ PASS: Toggle script exists and is executable
✓ PASS: Recording started successfully
✓ PASS: Recording stopped successfully
✓ PASS: Transcribed text found in clipboard
✓ PASS: No errors in recent logs
```

## Manual Testing Checklist

### 1. Basic Recording Test

**Prerequisites:**
- HyprSTT is running: `./run-dev.sh` or `./run.sh`
- Microphone is working: `arecord -d 2 test.wav && aplay test.wav`

**Steps:**
1. Press F9 (or run `./toggle-stt.sh`)
2. **Verify**: You should see notification "🎤 Recording started..."
3. Speak clearly: "This is a test of speech to text"
4. Press F9 again (or run `./toggle-stt.sh`)
5. **Verify**: You should see notification "⏹️ Processing speech..."
6. Wait 2-3 seconds for transcription
7. Check clipboard: `wl-paste`
8. **Expected**: Clipboard contains transcribed text

**If this fails:**
- Check logs: `tail -f ~/.local/share/hyprstt/logs/hyprstt.log`
- Check dev mode output if running with `./run-dev.sh`
- Verify state file: `cat ~/.local/share/hyprstt/state` (should toggle between "idle" and "recording")

### 2. Signal Handling Test

**Purpose:** Verify SIGUSR1 signals are being received and processed

**Steps:**
1. Start HyprSTT in dev mode: `./run-dev.sh`
2. In another terminal: `./toggle-stt.sh`
3. **Verify logs show**: `*** DEBUGGING: _toggle_recording called - is_recording=False, initialized=True`
4. **Verify logs show**: `*** DEBUGGING: Recording state changed from False to True`

**If no logs appear:**
- Signal handler may not be set up correctly
- Qt event loop may be blocking signals (check for QTimer setup in main.py:547)

### 3. State Synchronization Test

**Purpose:** Verify state file is synchronized correctly with actual recording state

**Steps:**
1. Start HyprSTT
2. Check initial state: `cat ~/.local/share/hyprstt/state` → Should be "idle"
3. Toggle recording: `./toggle-stt.sh`
4. Immediately check state: `cat ~/.local/share/hyprstt/state` → Should be "recording"
5. Toggle again: `./toggle-stt.sh`
6. Check state: `cat ~/.local/share/hyprstt/state` → Should be "idle"

**If state is wrong:**
- Check `_on_recording_changed()` callback in main.py:330
- Verify `_write_state()` is being called

### 4. Multiple Instance Test

**Purpose:** Ensure only one instance of HyprSTT is running

**Steps:**
1. Check running processes: `pgrep -fa "python -m src.main"`
2. **Expected**: Should see only ONE process
3. If multiple processes exist:
   - Stop all: `pkill -f "python -m src.main"`
   - Start fresh: `./run-dev.sh`

### 5. Transcription Quality Test

**Purpose:** Verify Whisper transcription is working with acceptable accuracy

**Test phrases** (speak clearly):
- "This is a test of speech to text functionality"
- "The quick brown fox jumps over the lazy dog"
- "Testing HyprSTT with various phrases and words"

**Steps:**
1. Start recording
2. Speak one of the test phrases
3. Stop recording
4. Check clipboard: `wl-paste`
5. **Verify**: Transcription is reasonably accurate (some errors are expected with tiny/base models)

**If transcription is poor:**
- Check which Whisper model is being used: `grep model_size ~/.config/hyprstt/config.yml`
- Consider upgrading to "small" or "medium" model for better accuracy
- Check audio levels: `pactl list sources | grep -A 10 "$(pactl get-default-source)"`

### 6. Clipboard Integration Test

**Purpose:** Verify text is being copied to clipboard correctly

**Steps:**
1. Clear clipboard: `echo "" | wl-copy`
2. Start recording, speak, stop recording
3. Wait for transcription (2-3 seconds)
4. Check clipboard: `wl-paste`
5. **Verify**: Clipboard contains transcribed text (not empty)

**If clipboard is empty:**
- Check `wl-copy` is installed: `which wl-copy`
- Check logs for "Text copied to clipboard" message
- Verify `WaylandInjector` in wayland_injector.py is working

## Common Issues and Solutions

### Issue: "Recording stopped" notification appears immediately

**Cause:** Toggle script was reading state file before Python updated it (race condition)

**Fix:** Removed state-based notifications from toggle-stt.sh (lines 68-84), letting Python handle notifications

**Verify fix:**
```bash
grep -A 5 "if kill -USR1" toggle-stt.sh
# Should NOT show notification logic, just comment about Python handling it
```

### Issue: No response when pressing F9 / running toggle script

**Cause:** Qt event loop blocking Python signal handlers

**Fix:** Added QTimer in main.py:547 to wake up event loop every 500ms

**Verify fix:**
```bash
grep -A 3 "QTimer" hyprstt/src/main.py
# Should see timer setup with 500ms interval
```

### Issue: Multiple HyprSTT instances running

**Cause:** Previous instances not being stopped properly

**Fix:**
```bash
# Stop all instances
pkill -f "python -m src.main"

# Verify all stopped
pgrep -f "python -m src.main"  # Should return nothing

# Start fresh instance
./run-dev.sh
```

### Issue: Transcription fails silently

**Cause:** Audio may be too quiet or silence

**Check debug recordings:**
```bash
ls ~/.local/share/hyprstt/debug/
# Failed recordings are saved here for analysis
```

**Solutions:**
- Increase microphone volume: `pactl set-source-volume @DEFAULT_SOURCE@ +10%`
- Lower audio thresholds in audio_capture.py (currently 50)
- Verify microphone is working: `arecord -d 5 test.wav && aplay test.wav`

## Testing After Changes

**Always test STT functionality after making changes to:**
- `main.py` (controller logic)
- `toggle-stt.sh` (toggle script)
- `audio_capture.py` (recording)
- `whisper_processor.py` (transcription)
- `wayland_injector.py` (clipboard)

**Quick test command:**
```bash
cd hyprstt && ./test-stt.sh
```

**Full manual test:**
1. Start in dev mode: `./run-dev.sh`
2. Toggle recording: `./toggle-stt.sh`
3. Speak test phrase
4. Toggle recording again
5. Check clipboard: `wl-paste`
6. Verify logs show no errors

## Regression Prevention

To prevent breaking STT functionality in the future:

1. **Before making changes:** Run `./test-stt.sh` to establish baseline
2. **After making changes:** Run `./test-stt.sh` again to verify functionality
3. **For Qt/event loop changes:** Pay special attention to signal handling
4. **For state management changes:** Verify state file synchronization
5. **For audio changes:** Test with various audio levels and durations

## Debug Mode Tips

When running in development mode (`./run-dev.sh`), you'll see detailed logs including:
- `*** DEBUGGING: _toggle_recording called` - Confirms signal received
- `*** DEBUGGING: Recording state changed` - Shows state transitions
- `*** DEBUGGING: Called audio_capture.start_recording()` - Confirms recording started
- Transcription results and clipboard operations

These debug messages are crucial for diagnosing issues.
