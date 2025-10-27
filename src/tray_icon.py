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
    def __init__(self, app: QApplication, on_exit: Optional[Callable] = None, font_size: int = 11):
        """
        Initialize the tray icon

        Args:
            app: QApplication instance
            on_exit: Callback function to call when Exit is clicked
            font_size: Font size for menu items (default: 11)
        """
        self.app = app
        self.on_exit = on_exit
        self.font_size = font_size
        self.tray_icon = None
        self.menu = None  # Keep reference to prevent garbage collection
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

        # Create the context menu (store as instance variable to prevent garbage collection)
        self.menu = QMenu()

        # Set window flags for better Wayland compatibility
        from PyQt6.QtCore import Qt
        self.menu.setWindowFlags(self.menu.windowFlags() | Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Set explicit font for the menu
        from PyQt6.QtGui import QFont
        menu_font = QFont("Sans", self.font_size)
        menu_font.setBold(False)
        self.menu.setFont(menu_font)

        # Set explicit styling to ensure visibility on Wayland
        self.menu.setStyleSheet(f"""
            QMenu {{
                background-color: white;
                color: black;
                border: 2px solid #444444;
                padding: 10px;
                font-family: Sans;
                font-size: {self.font_size}pt;
                min-width: 180px;
                min-height: 40px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                border: 1px solid transparent;
                background-color: white;
                color: black;
            }}
            QMenu::item:selected {{
                background-color: #0078d4;
                color: white;
            }}
        """)

        logger.debug("Creating context menu with Wayland-compatible styling")

        # Add "Exit HyprSTT" action with explicit font
        exit_action = QAction("Exit HyprSTT", self.menu)
        exit_action.setFont(menu_font)
        exit_action.triggered.connect(self._on_exit_clicked)
        self.menu.addAction(exit_action)

        # Set the context menu
        self.tray_icon.setContextMenu(self.menu)

        # Verify menu was set
        if self.tray_icon.contextMenu() is not None:
            logger.info("Context menu successfully attached to tray icon")
        else:
            logger.error("Failed to attach context menu to tray icon")

        # Connect signals for debugging
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.menu.aboutToShow.connect(self._on_menu_about_to_show)
        self.menu.aboutToHide.connect(self._on_menu_about_to_hide)

        logger.debug("Connected tray icon signals for event monitoring")

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

    def _on_tray_activated(self, reason):
        """Handle tray icon activation (clicks)"""
        from PyQt6.QtWidgets import QSystemTrayIcon
        from PyQt6.QtGui import QCursor

        logger.debug(f"Tray icon activated: {reason}")

        # Workaround for Hyprland: Manually show menu on any click
        # Hyprland's SNI implementation doesn't properly handle automatic context menus
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.Context):
            # Get cursor position (may be unreliable on Wayland)
            cursor_pos = QCursor.pos()

            # Try to get tray icon geometry as fallback
            tray_geometry = self.tray_icon.geometry()

            # Use tray icon position if cursor position is invalid (0, 0)
            if cursor_pos.x() == 0 and cursor_pos.y() == 0 and tray_geometry.isValid():
                # Position menu below the tray icon
                menu_pos = tray_geometry.bottomLeft()
                logger.debug(f"Using tray icon geometry for menu position")
            else:
                menu_pos = cursor_pos
                logger.debug(f"Using cursor position for menu")

            # Show menu
            self.menu.exec(menu_pos)

    def _on_menu_about_to_show(self):
        """Handle menu about to show"""
        logger.debug("Context menu opening")

    def _on_menu_about_to_hide(self):
        """Handle menu about to hide"""
        logger.debug("Context menu closing")

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
