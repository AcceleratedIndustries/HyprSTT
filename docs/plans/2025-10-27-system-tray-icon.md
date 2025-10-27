# System Tray Icon Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a system tray icon for HyprSTT with a right-click menu containing an "Exit HyprSTT" option.

**Architecture:** Create a new `TrayIcon` class using PyQt6's QSystemTrayIcon to provide a persistent system tray presence. The tray icon will integrate with the existing WhisperSTTController and provide graceful shutdown via the existing cleanup mechanism. The Qt event loop will run in the main thread alongside the existing application logic.

**Tech Stack:** PyQt6, QSystemTrayIcon, QMenu, QApplication

---

## Task 1: Add PyQt6 Dependency

**Files:**
- Modify: `/home/will/claude-stt/hyprstt/requirements.txt`

**Step 1: Add PyQt6 to requirements.txt**

Add the PyQt6 dependency after the existing dependencies:

```
PyQt6>=6.5.0
```

**Step 2: Verify the change**

Run: `cat /home/will/claude-stt/hyprstt/requirements.txt | grep PyQt6`
Expected: Output shows `PyQt6>=6.5.0`

**Step 3: Install the new dependency**

Run: `pip install PyQt6>=6.5.0`
Expected: PyQt6 installs successfully

**Step 4: Commit**

```bash
cd /home/will/claude-stt/hyprstt
git add requirements.txt
git commit -m "feat: add PyQt6 dependency for system tray icon

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Create TrayIcon Module

**Files:**
- Create: `/home/will/claude-stt/hyprstt/src/tray_icon.py`

**Step 1: Write the failing import test**

Run: `cd /home/will/claude-stt/hyprstt && python -c "from src.tray_icon import TrayIcon"`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.tray_icon'"

**Step 2: Create the tray_icon module with basic structure**

Create `/home/will/claude-stt/hyprstt/src/tray_icon.py`:

```python
import os
import sys
from typing import Callable, Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
from .utils import setup_logger

logger = setup_logger("hyprstt.tray_icon")

class TrayIcon:
    """
    System tray icon for HyprSTT with context menu
    """
    def __init__(self, app: QApplication, on_exit: Optional[Callable] = None):
        """
        Initialize the tray icon

        Args:
            app: QApplication instance
            on_exit: Callback function to call when Exit is clicked
        """
        self.app = app
        self.on_exit = on_exit
        self.tray_icon = None
        self._setup_tray_icon()

    def _setup_tray_icon(self):
        """Set up the system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray not available on this system")
            raise RuntimeError("System tray not available")

        # Create the tray icon
        self.tray_icon = QSystemTrayIcon(self.app)

        # Set the icon - use a default icon for now
        icon = self._get_icon()
        self.tray_icon.setIcon(icon)

        # Set tooltip
        self.tray_icon.setToolTip("HyprSTT - Speech to Text")

        # Create the context menu
        menu = QMenu()

        # Add "Exit HyprSTT" action
        exit_action = QAction("Exit HyprSTT", None)
        exit_action.triggered.connect(self._on_exit_clicked)
        menu.addAction(exit_action)

        # Set the context menu
        self.tray_icon.setContextMenu(menu)

        # Show the tray icon
        self.tray_icon.show()

        logger.info("System tray icon initialized")

    def _get_icon(self) -> QIcon:
        """
        Get the tray icon image

        Returns:
            QIcon instance
        """
        # For now, use a system theme icon
        # In production, we should bundle a custom icon
        icon = QIcon.fromTheme("audio-input-microphone")

        # Fallback if theme icon not available
        if icon.isNull():
            # Use a built-in Qt icon as fallback
            from PyQt6.QtWidgets import QStyle
            style = self.app.style()
            icon = style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)

        return icon

    def _on_exit_clicked(self):
        """Handle exit menu item click"""
        logger.info("Exit clicked from tray icon menu")

        # Call the exit callback if provided
        if self.on_exit:
            self.on_exit()
        else:
            # Default behavior: quit the application
            self.app.quit()

    def hide(self):
        """Hide the tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()

    def show(self):
        """Show the tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
```

**Step 3: Run import test to verify it passes**

Run: `cd /home/will/claude-stt/hyprstt && python -c "from src.tray_icon import TrayIcon; print('Success')"`
Expected: PASS with "Success" output

**Step 4: Commit**

```bash
cd /home/will/claude-stt/hyprstt
git add src/tray_icon.py
git commit -m "feat: create TrayIcon class with exit menu

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Integrate TrayIcon with Main Controller

**Files:**
- Modify: `/home/will/claude-stt/hyprstt/src/main.py`

**Step 1: Test that main.py currently runs without Qt**

Run: `cd /home/will/claude-stt/hyprstt && timeout 5 python -m src.main || echo "Timeout expected"`
Expected: Application starts or times out (we'll kill it after 5 seconds)

**Step 2: Add PyQt6 and TrayIcon imports**

In `/home/will/claude-stt/hyprstt/src/main.py`, after the line `from .utils import create_notification, get_config_path, setup_logger, check_dependencies` (line 22), add:

```python
from PyQt6.QtWidgets import QApplication
from .tray_icon import TrayIcon
```

**Step 3: Modify WhisperSTTController.__init__ to accept Qt app**

In `/home/will/claude-stt/hyprstt/src/main.py`, replace the `__init__` method (starting at line 31) with:

```python
def __init__(self, config_path: Optional[str] = None, qt_app: Optional[QApplication] = None):
    """
    Initialize the controller

    Args:
        config_path: Path to configuration file
        qt_app: QApplication instance for tray icon (optional)
    """
    # Load configuration
    self.config = self._load_config(config_path)

    # Store Qt app reference
    self.qt_app = qt_app
    self.tray_icon = None

    # Initialize state
    self.is_recording = False
    self.keyboard_listener_thread = None
    self.audio_capture = None
    self.whisper_processor = None
    self.text_injector = None
    self.initialized = False
    self.state_file = os.path.expanduser("~/.local/share/hyprstt/state")

    # Ensure state directory exists and initialize state
    os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
    self._write_state("idle")

    # Initialize components
    self._init_components()
```

**Step 4: Initialize tray icon in _init_components**

In `/home/will/claude-stt/hyprstt/src/main.py`, after line 202 (after the log message "Visual indicator disabled"), add:

```python

            # Initialize system tray icon if Qt app is available and enabled in config
            if self.qt_app and self.config["ui"].get("tray_icon", True):
                try:
                    logger.info("Initializing system tray icon...")
                    self.tray_icon = TrayIcon(
                        app=self.qt_app,
                        on_exit=self._handle_tray_exit
                    )
                    logger.info("System tray icon initialized successfully")
                except Exception as e:
                    logger.warning(f"System tray icon not available: {e}")
                    logger.info("Application will continue without tray icon")
                    self.tray_icon = None
            elif not self.config["ui"].get("tray_icon", True):
                logger.info("System tray icon disabled in configuration")
```

**Step 5: Add tray exit handler method**

In `/home/will/claude-stt/hyprstt/src/main.py`, after the `_on_recording_changed` method (around line 331), add:

```python

    def _handle_tray_exit(self):
        """Handle exit request from system tray"""
        logger.info("Exit requested from system tray")

        # Show notification
        if self.config["ui"]["notifications"]:
            create_notification(
                "HyprSTT",
                "Shutting down...",
                timeout=2
            )

        # Clean up and exit
        self.cleanup()

        # Quit Qt application if available
        if self.qt_app:
            self.qt_app.quit()
        else:
            sys.exit(0)
```

**Step 6: Update cleanup method to hide tray icon**

In `/home/will/claude-stt/hyprstt/src/main.py`, in the `cleanup` method (around line 513), before the line `logger.info("System shutdown complete")`, add:

```python

            # Hide tray icon
            if self.tray_icon:
                self.tray_icon.hide()
```

**Step 7: Update run method to use Qt event loop**

In `/home/will/claude-stt/hyprstt/src/main.py`, replace the `run` method (lines 477-502) with:

```python
    def run(self):
        """Run the controller"""
        if not self.initialized:
            logger.error("System not initialized")
            return False

        logger.info("System running - Press Ctrl+C to exit")

        # Show startup notification
        if self.config["ui"]["notifications"]:
            hotkey_str = "+".join(self.config["hotkeys"]["toggle_recording"])
            create_notification(
                "HyprSTT",
                f"Running - Use {hotkey_str} to toggle recording",
                timeout=5
            )

        # If Qt app is available, use Qt event loop
        if self.qt_app:
            logger.info("Starting Qt event loop")
            try:
                return self.qt_app.exec() == 0
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, exiting...")
                return self.cleanup()
        else:
            # Keep the main thread alive (original behavior)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, exiting...")
                return self.cleanup()

        return True
```

**Step 8: Update main() function to create Qt app**

In `/home/will/claude-stt/hyprstt/src/main.py`, replace the `main()` function (lines 523-543) with:

```python
def main():
    """Main entry point"""
    # Initialize Qt Application for system tray
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when windows close
    app.setApplicationName("HyprSTT")

    # Create controller with Qt app
    controller = WhisperSTTController(qt_app=app)

    # Handle termination signals
    def signal_handler(sig, frame):
        print("\nShutting down...")
        controller.cleanup()
        app.quit()
        sys.exit(0)

    # Handle toggle signal
    def toggle_handler(sig, frame):
        print("Toggle signal received")
        controller._toggle_recording()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, toggle_handler)  # Add SIGUSR1 for external toggle

    # Run the controller
    sys.exit(0 if controller.run() else 1)
```

**Step 9: Test the integration**

Run: `cd /home/will/claude-stt/hyprstt && timeout 10 python -m src.main`
Expected: Application starts with tray icon visible (or warning if no tray available)

**Step 10: Commit**

```bash
cd /home/will/claude-stt/hyprstt
git add src/main.py
git commit -m "feat: integrate system tray icon with main controller

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Add Configuration Options

**Files:**
- Modify: `/home/will/claude-stt/hyprstt/config/config.yml`
- Modify: `/home/will/claude-stt/hyprstt/src/main.py`

**Step 1: Add tray icon config option**

In `/home/will/claude-stt/hyprstt/config/config.yml`, modify the `ui` section to add tray_icon option:

```yaml
ui:
  notifications: true  # Enable desktop notifications
  notification_timeout: 2  # Notification display time in seconds
  tray_icon: true  # Enable system tray icon
```

**Step 2: Update default config in main.py**

In `/home/will/claude-stt/hyprstt/src/main.py`, in the `_load_config` method (around line 86-89), update the "ui" section:

```python
            "ui": {
                "notifications": True,
                "notification_timeout": 2,
                "tray_icon": True
            }
```

**Step 3: Test with configuration option**

Run: `cd /home/will/claude-stt/hyprstt && timeout 5 python -m src.main`
Expected: Application starts with tray icon (or appropriate log message)

**Step 4: Commit configuration option**

```bash
cd /home/will/claude-stt/hyprstt
git add config/config.yml src/main.py
git commit -m "feat: add configuration option for system tray icon

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Update Documentation

**Files:**
- Modify: `/home/will/claude-stt/hyprstt/README.md`
- Modify: `/home/will/claude-stt/CLAUDE.md`

**Step 1: Add tray icon to README features**

In `/home/will/claude-stt/hyprstt/README.md`, find the features section and add a line about the system tray icon.

**Step 2: Update README dependencies**

In `/home/will/claude-stt/hyprstt/README.md`, add PyQt6 to the dependencies list.

**Step 3: Add tray icon usage section**

In `/home/will/claude-stt/hyprstt/README.md`, add a new section explaining the tray icon:

```markdown
### System Tray

HyprSTT runs with a system tray icon for easy access:

- **Icon**: Look for the microphone icon in your system tray
- **Right-click menu**: Right-click the icon to access options
- **Exit**: Select "Exit HyprSTT" to gracefully shut down the application

To disable the tray icon, set `tray_icon: false` in your config file.
```

**Step 4: Update CLAUDE.md**

In `/home/will/claude-stt/CLAUDE.md`, add information about the tray_icon component in the "Key Components" section:

```markdown
- `tray_icon.py`: System tray icon with exit menu (PyQt6-based)
```

**Step 5: Verify documentation changes**

Run: `cd /home/will/claude-stt/hyprstt && git diff`
Expected: Shows the documentation additions

**Step 6: Commit documentation updates**

```bash
cd /home/will/claude-stt/hyprstt
git add README.md
cd /home/will/claude-stt
git add CLAUDE.md
cd /home/will/claude-stt/hyprstt
git commit -m "docs: add system tray icon documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Final Integration Testing

**Files:**
- Test: Full end-to-end testing

**Step 1: Clean any running instances**

Run: `pkill -f "python -m src.main"`
Expected: Any running instances are stopped

**Step 2: Start application with development script**

Run: `cd /home/will/claude-stt/hyprstt && ./run-dev.sh &`
Expected: Application starts with log output

**Step 3: Verify tray icon is present**

Check: Look for the microphone icon in your system tray
Expected: Icon is visible with tooltip "HyprSTT - Speech to Text"

**Step 4: Test right-click menu**

Action: Right-click on the tray icon
Expected: Context menu appears with "Exit HyprSTT" option

**Step 5: Test exit functionality**

Action: Click "Exit HyprSTT" in the menu
Expected:
- Notification appears: "Shutting down..."
- Application exits cleanly
- Tray icon disappears

**Step 6: Verify no processes remain**

Run: `ps aux | grep "python -m src.main" | grep -v grep`
Expected: No output (process has exited)

**Step 7: Check logs for errors**

Run: `tail -n 50 ~/.local/share/hyprstt/logs/hyprstt.log`
Expected: Clean shutdown messages, no errors

**Step 8: Test with tray disabled**

Edit `~/.config/hyprstt/config.yml` to set `tray_icon: false`
Run: `cd /home/will/claude-stt/hyprstt && timeout 5 python -m src.main`
Expected: Application starts without tray icon, logs message about tray being disabled

**Step 9: Re-enable tray and test production mode**

Edit config back to `tray_icon: true`
Run: `cd /home/will/claude-stt/hyprstt && ./run.sh`
Expected: Application starts in background with tray icon

**Step 10: Final cleanup and verification**

Test exit from tray one more time, verify everything works as expected

---

## Testing Checklist

**Functionality:**
- [ ] Tray icon appears in system tray
- [ ] Right-click shows context menu
- [ ] "Exit HyprSTT" menu item functions correctly
- [ ] Application exits cleanly when using tray exit
- [ ] No orphaned processes after exit
- [ ] Config option to enable/disable tray works
- [ ] Gracefully handles systems without tray support

**Integration:**
- [ ] Speech recording still works with tray active
- [ ] Transcription works normally
- [ ] Hotkeys still function
- [ ] Notifications still work
- [ ] Logs show appropriate messages

**Edge Cases:**
- [ ] Works when system tray is not available (logs warning)
- [ ] Works when config disables tray
- [ ] Works with both run.sh and run-dev.sh
- [ ] Clean shutdown via Ctrl+C still works
- [ ] Clean shutdown via kill signal still works

---

## Future Enhancements

Potential additions for future iterations (not in this plan):

1. **Custom Icon**: Create and bundle a custom HyprSTT icon file
2. **Recording Status**: Change icon appearance when recording is active
3. **Additional Menu Items**:
   - Toggle recording from tray menu
   - Open settings/config
   - View recent transcriptions
   - Show/hide notifications
4. **Click Actions**: Define left-click and double-click behaviors
5. **Status Messages**: Show current state in tooltip

---

## Rollback Instructions

If issues arise and you need to rollback:

**Via Git:**
```bash
cd /home/will/claude-stt/hyprstt
git log --oneline -10  # Find the commit before tray icon work
git revert <commit-hash>..HEAD
pip uninstall PyQt6
```

**Via Configuration:**
Set in `~/.config/hyprstt/config.yml`:
```yaml
ui:
  tray_icon: false
```

**Manual Removal:**
```bash
cd /home/will/claude-stt/hyprstt
git checkout main
git pull
rm src/tray_icon.py
# Restore original main.py from git
```
