import subprocess
import time
from typing import Optional

class WaylandInjector:
    """
    Module for handling transcribed text - now only uses clipboard and notifications
    and does not attempt to type into applications directly
    """
    
    def __init__(self):
        """Initialize the injector"""
        # No longer using any keyboard injection tools
        self.use_wtype = False  # Explicitly set to False to disable typing
        self.use_ydotool = False  # Explicitly set to False to disable typing
        
        # Check if clipboard tool is available
        try:
            subprocess.run(["which", "wl-copy"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.clipboard_available = True
        except subprocess.CalledProcessError:
            self.clipboard_available = False
            print("Warning: wl-copy not available. Clipboard functionality will be limited.")
    
    # These methods are kept for backward compatibility but are never used
    def _check_wtype_available(self) -> bool:
        return False
    
    def _check_ydotool_available(self) -> bool:
        return False
    
    def inject_text(self, text: str, delay: float = 0.0):
        """
        Copy text to clipboard and show notification
        
        Args:
            text: Text to copy to clipboard
            delay: Delay in seconds between text copying and previous action
        """
        if not text:
            return
            
        if delay > 0:
            time.sleep(delay)
        
        import os
        import tempfile
        
        # Create a notification instead of typing directly
        try:
            # First, copy to clipboard for manual pasting
            try:
                subprocess.run(["wl-copy", text], check=True)
                print(f"Text copied to clipboard: '{text[:30]}...'")
            except Exception as e:
                print(f"Failed to copy to clipboard: {e}")
            
            # Create a notification with the transcribed text
            try:
                subprocess.run([
                    "notify-send", 
                    "--expire-time=10000",  # 10 seconds
                    "--urgency=normal",
                    "Whisper Transcription (copied to clipboard)",
                    text
                ], check=True, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print("Notification service unavailable - text copied to clipboard only")
            
            print("Sent notification with transcribed text and copied to clipboard")
            return
                
        except Exception as e:
            print(f"Notification and clipboard method failed: {e}")
            import traceback
            traceback.print_exc()
    
    def inject_keystrokes(self, key: str):
        """
        This method is disabled - keyboard injection is no longer used
        
        Args:
            key: Key (not used)
        """
        # This method is intentionally disabled
        print(f"Keystroke injection is disabled - would have pressed {key}")
    
    def press_enter(self):
        """This method is disabled"""
        print("Enter key press is disabled")
    
    def press_tab(self):
        """This method is disabled"""
        print("Tab key press is disabled")
    
    def press_escape(self):
        """This method is disabled"""
        print("Escape key press is disabled")
    
    def press_backspace(self, count: int = 1):
        """
        This method is disabled
        
        Args:
            count: Number of times (not used)
        """
        print(f"Backspace key press is disabled (count: {count})")
            
    def press_key_combination(self, keys: list):
        """
        This method is disabled
        
        Args:
            keys: List of keys to press (not used)
        """
        print(f"Key combination is disabled - would have pressed {'+'.join(keys)}")