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
