import os
import json
import socket
import subprocess
from typing import Optional, Dict, List

class HyprlandManager:
    """
    Hyprland window manager module for detecting focused window and window properties
    using Hyprland IPC
    """
    
    @staticmethod
    def get_hyprland_socket_path() -> Optional[str]:
        """
        Get the path to the Hyprland IPC socket
        
        Returns:
            Socket path or None if not found
        """
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if not signature:
            print("Warning: HYPRLAND_INSTANCE_SIGNATURE environment variable not set.")
            print("Trying to find Hyprland socket manually...")
            
            # Try to find the socket in /run/user/1000/hypr directory
            try:
                hypr_dir = "/run/user/1000/hypr"
                if os.path.isdir(hypr_dir):
                    for sig_dir in os.listdir(hypr_dir):
                        socket_path = os.path.join(hypr_dir, sig_dir, ".socket.sock")
                        if os.path.exists(socket_path):
                            print(f"Found Hyprland socket at: {socket_path}")
                            return socket_path

                # Fall back to /tmp/hypr if not found in /run/user/1000/hypr
                hypr_dir = "/tmp/hypr"
                if os.path.isdir(hypr_dir):
                    for sig_dir in os.listdir(hypr_dir):
                        socket_path = os.path.join(hypr_dir, sig_dir, ".socket.sock")
                        if os.path.exists(socket_path):
                            print(f"Found Hyprland socket at: {socket_path}")
                            return socket_path
            except Exception as e:
                print(f"Error searching for Hyprland socket: {e}")
            
            return None
            
        socket_path = f"/run/user/1000/hypr/{signature}/.socket.sock"
        if not os.path.exists(socket_path):
            # Fall back to /tmp/hypr path
            socket_path = f"/tmp/hypr/{signature}/.socket.sock"
        if not os.path.exists(socket_path):
            print(f"Warning: Hyprland socket not found at {socket_path}")
            return None
            
        return socket_path
    
    @staticmethod
    def get_focused_window() -> Optional[Dict[str, any]]:
        """
        Get information about the currently focused window using hyprctl
        
        Returns:
            Dictionary with window information or None if failed
        """
        try:
            # Get active window info using hyprctl
            try:
                result = subprocess.check_output(
                    ["hyprctl", "activewindow", "-j"],
                    universal_newlines=True
                )
            except subprocess.CalledProcessError:
                print("Failed to get active window with hyprctl")
                return None
            
            try:
                window_info = json.loads(result)
            except json.JSONDecodeError:
                print("Failed to parse hyprctl output as JSON")
                return None
            
            # Check if we have a valid window (empty object means no window focused)
            if not window_info or "address" not in window_info:
                return None
                
            return {
                "id": window_info.get("address", ""),  # Memory address as ID
                "class": window_info.get("class", ""),
                "title": window_info.get("title", ""),
                "pid": window_info.get("pid", 0),
                "workspace": window_info.get("workspace", {}).get("id", 0),
                "size": {
                    "width": window_info.get("size", [0, 0])[0] if isinstance(window_info.get("size"), list) else 0,
                    "height": window_info.get("size", [0, 0])[1] if isinstance(window_info.get("size"), list) else 0
                },
                "position": {
                    "x": window_info.get("at", [0, 0])[0] if isinstance(window_info.get("at"), list) else 0,
                    "y": window_info.get("at", [0, 0])[1] if isinstance(window_info.get("at"), list) else 0
                }
            }
        except Exception as e:
            print(f"Unexpected error getting focused window: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def is_terminal(window_info: Dict[str, any]) -> bool:
        """
        Determine if the window is a terminal
        
        Args:
            window_info: Window information from get_focused_window
            
        Returns:
            True if the window is a terminal, False otherwise
        """
        terminal_classes = [
            "foot", "kitty", "alacritty", "termite", "wezterm",
            "terminal", "xterm", "gnome-terminal", "konsole", 
            "xfce4-terminal", "terminator", "urxvt", "rxvt",
            "tilix", "terminology", "st-256color"
        ]
        
        window_class = window_info.get("class", "").lower()
        window_title = window_info.get("title", "").lower()
        
        # Check if window class matches any known terminal
        if any(term in window_class for term in terminal_classes):
            return True
            
        # Check window title for terminal indicators
        terminal_indicators = ["terminal", "console", "shell", "bash", "zsh", "fish"]
        if any(indicator in window_title for indicator in terminal_indicators):
            return True
            
        return False
    
    @staticmethod
    def is_text_input(window_info: Dict[str, any]) -> bool:
        """
        Try to determine if the focused element is a text input
        
        Args:
            window_info: Window information from get_focused_window
            
        Returns:
            True if the window likely has a text input focused, False otherwise
        """
        # Known text editors and IDEs
        text_editor_classes = [
            "code", "atom", "sublime_text", "gedit", "kate", "gvim", 
            "emacs", "mousepad", "leafpad", "pluma", "geany", "pycharm",
            "intellij", "eclipse", "netbeans", "vstudio", "helix", "neovide"
        ]
        
        # Known applications with text input fields
        text_input_classes = [
            "firefox", "chrome", "chromium", "brave-browser", "opera", "safari",
            "thunderbird", "evolution", "geary", "libreoffice", 
            "soffice", "abiword", "gimp", "inkscape", "discord",
            "slack", "telegram", "signal", "whatsapp", "polkit-gnome-authentication-agent-1"
        ]
        
        window_class = window_info.get("class", "").lower()
        
        # Check if window is a terminal (which accepts text input)
        if HyprlandManager.is_terminal(window_info):
            return True
            
        # Check if window is a text editor or IDE
        if any(editor in window_class for editor in text_editor_classes):
            return True
            
        # Check if window is an application that likely has text input
        if any(app in window_class for app in text_input_classes):
            return True
            
        return False
    
    @staticmethod
    def get_all_windows() -> List[Dict[str, any]]:
        """
        Get list of all windows currently managed by Hyprland
        
        Returns:
            List of window information dictionaries
        """
        try:
            # Get all clients using hyprctl
            result = subprocess.check_output(
                ["hyprctl", "clients", "-j"],
                universal_newlines=True
            )
            
            windows = json.loads(result)
            
            return [{
                "id": window.get("address", ""),
                "class": window.get("class", ""),
                "title": window.get("title", ""),
                "pid": window.get("pid", 0),
                "workspace": window.get("workspace", {}).get("id", 0),
                "size": {
                    "width": window.get("size", [0, 0])[0],
                    "height": window.get("size", [0, 0])[1]
                },
                "position": {
                    "x": window.get("at", [0, 0])[0],
                    "y": window.get("at", [0, 0])[1]
                }
            } for window in windows]
        except Exception as e:
            print(f"Error getting all windows: {e}")
            return []
    
    @staticmethod
    def send_command(command: str) -> bool:
        """
        Send a command to Hyprland through the socket
        
        Args:
            command: Hyprland command to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try using hyprctl first
            try:
                subprocess.run(
                    ["hyprctl", "dispatch", command],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("hyprctl dispatch failed, trying socket method")
            
            # Fall back to socket method
            socket_path = HyprlandManager.get_hyprland_socket_path()
            if not socket_path:
                print("Error: Could not find Hyprland socket")
                return False
                
            # Use socat to send command to socket
            subprocess.run(
                ["socat", "-", socket_path],
                input=command.encode(),
                check=True
            )
            return True
        except Exception as e:
            print(f"Error sending command to Hyprland: {e}")
            return False
    
    @staticmethod
    def activate_window(window_id: str) -> bool:
        """
        Activate (focus) a window by its ID
        
        Args:
            window_id: Window ID (address)
            
        Returns:
            True if successful, False otherwise
        """
        if not window_id:
            return False
            
        return HyprlandManager.send_command(f"focuswindow address:{window_id}")
    
    @staticmethod
    def get_hyprland_event_socket_path() -> Optional[str]:
        """
        Get the path to the Hyprland event socket
        
        Returns:
            Socket path or None if not found
        """
        signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if not signature:
            print("Warning: HYPRLAND_INSTANCE_SIGNATURE environment variable not set.")
            print("Trying to find Hyprland event socket manually...")
            
            # Try to find the socket in /run/user/1000/hypr directory
            try:
                hypr_dir = "/run/user/1000/hypr"
                if os.path.isdir(hypr_dir):
                    for sig_dir in os.listdir(hypr_dir):
                        socket_path = os.path.join(hypr_dir, sig_dir, ".socket2.sock")
                        if os.path.exists(socket_path):
                            print(f"Found Hyprland event socket at: {socket_path}")
                            return socket_path

                # Fall back to /tmp/hypr if not found in /run/user/1000/hypr
                hypr_dir = "/tmp/hypr"
                if os.path.isdir(hypr_dir):
                    for sig_dir in os.listdir(hypr_dir):
                        socket_path = os.path.join(hypr_dir, sig_dir, ".socket2.sock")
                        if os.path.exists(socket_path):
                            print(f"Found Hyprland event socket at: {socket_path}")
                            return socket_path
            except Exception as e:
                print(f"Error searching for Hyprland event socket: {e}")
            
            return None
            
        socket_path = f"/run/user/1000/hypr/{signature}/.socket2.sock"
        if not os.path.exists(socket_path):
            # Fall back to /tmp/hypr path
            socket_path = f"/tmp/hypr/{signature}/.socket2.sock"
        if not os.path.exists(socket_path):
            print(f"Warning: Hyprland event socket not found at {socket_path}")
            return None
            
        return socket_path
    
    @staticmethod
    def listen_for_events(callback):
        """
        Listen for Hyprland events (async)
        
        Args:
            callback: Function to call with event data
        """
        try:
            socket_path = HyprlandManager.get_hyprland_event_socket_path()
            if not socket_path:
                print("Error: Could not find Hyprland event socket. Using direct keyboard monitoring instead.")
                # TODO: Implement fallback to direct keyboard monitoring
                return None
                
            def listener():
                try:
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(socket_path)
                    print(f"Connected to Hyprland event socket at {socket_path}")
                    
                    while True:
                        try:
                            data = sock.recv(1024).decode().strip()
                            if data:
                                callback(data)
                        except Exception as e:
                            print(f"Error in event listener: {e}")
                            break
                            
                    sock.close()
                except Exception as e:
                    print(f"Error connecting to Hyprland event socket: {e}")
                
            import threading
            thread = threading.Thread(target=listener, daemon=True)
            thread.start()
            return thread
        except Exception as e:
            print(f"Error setting up event listener: {e}")
            return None