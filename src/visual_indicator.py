import json
import os
import subprocess
import threading
import time
from typing import Optional

class VisualIndicator:
    """
    Visual indicator for STT activity using Hyprland overlay
    """
    def __init__(self, config=None):
        """
        Initialize the visual indicator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.active = False
        self.thread = None
        self.stop_event = threading.Event()
        
        # Default configuration
        self.indicator_type = self.config.get("type", "overlay")
        self.position = self.config.get("position", "top-right")
        self.size = self.config.get("size", "small")
        self.color = self.config.get("color", "#ff0000")
        self.opacity = self.config.get("opacity", 0.7)
        self.pulse = self.config.get("pulse", True)
        
        # Size mapping
        self.size_map = {
            "small": (50, 50),
            "medium": (100, 100),
            "large": (150, 150),
        }
        
        # Position mapping (offset from edge in pixels)
        self.position_map = {
            "top-left": (20, 20),
            "top-right": (-70, 20),
            "bottom-left": (20, -70),
            "bottom-right": (-70, -70),
            "top-center": ("center", 20),
            "bottom-center": ("center", -70),
        }
        
    def _create_overlay_window(self):
        """Create overlay window using Hyprland special workspace"""
        try:
            # Get screen dimensions
            monitors = self._get_monitors()
            if not monitors:
                return False
            
            # Use primary monitor
            monitor = next((m for m in monitors if m.get("active")), monitors[0])
            width, height = monitor.get("width", 1920), monitor.get("height", 1080)
            
            # Calculate position
            overlay_width, overlay_height = self.size_map.get(self.size, (50, 50))
            pos_x, pos_y = self.position_map.get(self.position, (20, 20))
            
            if pos_x == "center":
                pos_x = (width - overlay_width) // 2
            elif pos_x < 0:
                pos_x = width + pos_x  # Negative values are from right edge
                
            if pos_y == "center":
                pos_y = (height - overlay_height) // 2
            elif pos_y < 0:
                pos_y = height + pos_y  # Negative values are from bottom edge
            
            # Create special workspace for overlay
            subprocess.run(["hyprctl", "dispatch", "exec", "kitty --class=stt_indicator"])
            time.sleep(0.2)  # Wait for window to appear
            
            # Configure window
            subprocess.run(["hyprctl", "dispatch", "movetoworkspacesilent", "special:stt_indicator", "address:$(hyprctl activewindow -j | jq -r .address)"])
            subprocess.run(["hyprctl", "dispatch", "resizewindowpixel", f"exact {overlay_width} {overlay_height}", "address:$(hyprctl clients -j | jq -r '.[] | select(.class==\"stt_indicator\") | .address')"])
            subprocess.run(["hyprctl", "dispatch", "movewindowpixel", f"exact {pos_x} {pos_y}", "address:$(hyprctl clients -j | jq -r '.[] | select(.class==\"stt_indicator\") | .address')"])
            
            # Set appearance
            subprocess.run(["hyprctl", "keyword", "windowrulev2", f"opacity {self.opacity} {self.opacity},class:^(stt_indicator)$"])
            subprocess.run(["hyprctl", "keyword", "windowrulev2", "noshadow,class:^(stt_indicator)$"])
            subprocess.run(["hyprctl", "keyword", "windowrulev2", "noborder,class:^(stt_indicator)$"])
            subprocess.run(["hyprctl", "keyword", "windowrulev2", "noinitialfocus,class:^(stt_indicator)$"])
            
            return True
        except Exception as e:
            print(f"Error creating overlay: {e}")
            return False
    
    def _get_monitors(self):
        """Get monitor information from Hyprland"""
        try:
            output = subprocess.check_output(["hyprctl", "monitors", "-j"], universal_newlines=True)
            import json
            monitors = json.loads(output)
            return monitors
        except Exception:
            return []
    
    def _remove_overlay_window(self):
        """Remove the overlay window"""
        try:
            # First check if there's actually a window with this class before trying to close it
            result = subprocess.run(
                ["hyprctl", "clients", "-j"],
                capture_output=True, text=True, check=True
            )
            clients = json.loads(result.stdout)
            stt_windows = [client for client in clients if client.get("class") == "stt_indicator"]

            if stt_windows:
                # Only close if we found actual stt_indicator windows
                subprocess.run(["hyprctl", "dispatch", "closewindow", "class:stt_indicator"])
                print(f"Closed {len(stt_windows)} stt_indicator window(s)")
            else:
                print("No stt_indicator windows found to close")

            # Clean up workspace rules
            subprocess.run(["hyprctl", "keyword", "windowrulev2", "remove,class:^(stt_indicator)$"])
        except Exception as e:
            print(f"Error removing overlay: {e}")
    
    def show(self):
        """Show the visual indicator"""
        if self.active:
            return
        
        self.active = True
        self.stop_event.clear()
        
        if self.indicator_type == "overlay":
            success = self._create_overlay_window()
            if not success:
                self.active = False
                return
            
            # If pulsing effect is enabled, start pulse thread
            if self.pulse:
                self.thread = threading.Thread(target=self._pulse_effect, daemon=True)
                self.thread.start()
    
    def hide(self):
        """Hide the visual indicator"""
        if not self.active:
            return
        
        self.active = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.indicator_type == "overlay":
            self._remove_overlay_window()
    
    def _pulse_effect(self):
        """Create pulsing effect by changing opacity"""
        try:
            base_opacity = self.opacity
            min_opacity = base_opacity * 0.3
            step = 0.05
            direction = -1  # Start by decreasing
            current_opacity = base_opacity
            
            while not self.stop_event.is_set():
                # Update opacity
                current_opacity += direction * step
                
                # Check bounds and reverse direction if needed
                if current_opacity <= min_opacity:
                    current_opacity = min_opacity
                    direction = 1
                elif current_opacity >= base_opacity:
                    current_opacity = base_opacity
                    direction = -1
                
                # Apply new opacity
                subprocess.run(["hyprctl", "keyword", "windowrulev2", f"opacity {current_opacity} {current_opacity},class:^(stt_indicator)$"])
                
                # Sleep a bit
                time.sleep(0.1)
        except Exception as e:
            print(f"Error in pulse effect: {e}")
    
    def toggle(self):
        """Toggle the visual indicator"""
        if self.active:
            self.hide()
        else:
            self.show()