import threading
import time
from typing import Callable, List, Set, Optional
import logging

# Configure logger
logger = logging.getLogger("whisper_stt")

class KeyboardListener:
    """
    Keyboard listener implementation with multiple backend options
    """
    
    def __init__(self, callback: Callable, keys: List[str]):
        """
        Initialize keyboard listener
        
        Args:
            callback: Function to call when hotkey is pressed
            keys: List of keys in the hotkey combo (e.g. ["SUPER", "SPACE"])
        """
        self.callback = callback
        self.keys = [k.upper() for k in keys]
        self.thread = None
        self.running = False
        
    def start(self):
        """Start the keyboard listener"""
        if self.thread is not None:
            return
            
        self.running = True
        backend = self._detect_best_backend()
        
        if backend == "pynput":
            self.thread = threading.Thread(
                target=self._pynput_listener,
                daemon=True
            )
        elif backend == "evdev":
            self.thread = threading.Thread(
                target=self._evdev_listener,
                daemon=True
            )
        else:
            logger.error("No suitable keyboard listener backend found")
            return None
            
        self.thread.start()
        return self.thread
        
    def stop(self):
        """Stop the keyboard listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _detect_best_backend(self) -> str:
        """Detect the best available keyboard listener backend"""
        # Try pynput first (doesn't require root)
        try:
            import pynput
            return "pynput"
        except ImportError:
            logger.warning("pynput not installed, trying evdev")
            
        # Try evdev (might require root)
        try:
            import evdev
            return "evdev"
        except ImportError:
            logger.warning("evdev not installed")
            
        # No suitable backend found
        return "none"
    
    def _pynput_listener(self):
        """Keyboard listener using pynput"""
        try:
            from pynput import keyboard
            
            # Map key names to pynput key objects
            key_mapping = {
                "CTRL": keyboard.Key.ctrl,
                "SHIFT": keyboard.Key.shift,
                "ALT": keyboard.Key.alt,
                "SUPER": keyboard.Key.cmd,
                "SPACE": keyboard.Key.space,
                "ESCAPE": keyboard.Key.esc,
                "TAB": keyboard.Key.tab,
                "RETURN": keyboard.Key.enter,
                "BACKSPACE": keyboard.Key.backspace,
            }
            
            # Create set of keys to monitor
            hotkey_keys = set()
            for key in self.keys:
                if key in key_mapping:
                    hotkey_keys.add(key_mapping[key])
                else:
                    # For letters, numbers, etc.
                    try:
                        hotkey_keys.add(keyboard.KeyCode.from_char(key.lower()))
                    except:
                        logger.warning(f"Unable to map key: {key}")
            
            # Track currently pressed keys
            pressed_keys = set()
            
            def on_press(key):
                if not self.running:
                    return False
                
                pressed_keys.add(key)
                
                # Check if all hotkey keys are pressed
                if all(k in pressed_keys for k in hotkey_keys):
                    logger.info(f"Hotkey detected: {self.keys}")
                    self.callback()
                    
                    # Wait for keys to be released
                    time.sleep(0.1)
                    pressed_keys.clear()
            
            def on_release(key):
                if key in pressed_keys:
                    pressed_keys.remove(key)
                    
                if not self.running:
                    return False
            
            # Start listener
            logger.info(f"Starting pynput keyboard listener for keys: {self.keys}")
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
                
        except Exception as e:
            logger.error(f"Error in pynput keyboard listener: {e}")
    
    def _evdev_listener(self):
        """Keyboard listener using evdev"""
        try:
            import evdev
            from select import select
            
            def find_keyboard_devices():
                """Find keyboard devices"""
                devices = []
                for path in evdev.list_devices():
                    try:
                        device = evdev.InputDevice(path)
                        caps = device.capabilities()
                        
                        # Must have EV_KEY capability
                        if evdev.ecodes.EV_KEY not in caps:
                            continue
                            
                        # Check if it's actually a keyboard by looking for common keyboard keys
                        key_codes = caps.get(evdev.ecodes.EV_KEY, [])
                        has_letters = any(code >= evdev.ecodes.KEY_Q and code <= evdev.ecodes.KEY_P for code in key_codes)
                        has_space = evdev.ecodes.KEY_SPACE in key_codes
                        
                        # Exclude devices that are clearly not keyboards
                        name_lower = device.name.lower()
                        if any(exclude in name_lower for exclude in ['mouse', 'touchpad', 'trackpoint', 'button', 'logitech', 'mx ']):
                            logger.debug(f"Excluded non-keyboard device: {device.name}")
                            continue
                            
                        # Include if it has keyboard-like characteristics
                        if "keyboard" in name_lower or (has_letters and has_space):
                            devices.append(device)
                            logger.info(f"Found keyboard device: {device.name} at {path}")
                        else:
                            logger.debug(f"Excluded device: {device.name} at {path}")
                    except Exception:
                        continue
                return devices
            
            # Map key names to evdev key codes
            key_mapping = {
                "CTRL": "KEY_LEFTCTRL",
                "SHIFT": "KEY_LEFTSHIFT",
                "ALT": "KEY_LEFTALT",
                "SUPER": "KEY_LEFTMETA",
                "SPACE": "KEY_SPACE",
                "ESCAPE": "KEY_ESC",
                "TAB": "KEY_TAB",
                "RETURN": "KEY_ENTER",
                "BACKSPACE": "KEY_BACKSPACE",
            }
            
            # Initialize device list
            devices = find_keyboard_devices()
            if not devices:
                logger.error("No keyboard devices found")
                return
                
            logger.info(f"Monitoring {len(devices)} keyboard devices")
            
            # Track key states
            pressed_keys = set()
            toggle_keys = set()
            
            # Convert key names to evdev key names
            for key in self.keys:
                if key in key_mapping:
                    toggle_keys.add(key_mapping[key])
                else:
                    # For letters, numbers, etc.
                    toggle_keys.add(f"KEY_{key}")
            
            # Main event loop
            while self.running:
                r, w, x = select(devices, [], [], 0.1)
                for device in r:
                    try:
                        for event in device.read():
                            if event.type == evdev.ecodes.EV_KEY:
                                key_event = evdev.categorize(event)
                                # Skip mouse button events (codes 272-279 are mouse buttons)
                                if key_event.scancode >= 272 and key_event.scancode <= 279:
                                    continue
                                    
                                # Skip if scancode not in KEY mapping
                                if key_event.scancode not in evdev.ecodes.KEY:
                                    continue
                                    
                                key_name = evdev.ecodes.KEY[key_event.scancode]
                                
                                if key_event.keystate == key_event.key_down:
                                    pressed_keys.add(key_name)
                                elif key_event.keystate == key_event.key_up:
                                    if key_name in pressed_keys:
                                        pressed_keys.remove(key_name)
                                
                                # Check if hotkey combination is pressed
                                if toggle_keys.issubset(pressed_keys):
                                    logger.info(f"Hotkey detected: {self.keys}")
                                    self.callback()
                                    
                                    # Wait until keys released to avoid multiple triggers
                                    while toggle_keys.intersection(pressed_keys):
                                        time.sleep(0.05)
                                        pressed_keys = set()
                    except Exception as e:
                        logger.error(f"Error reading keyboard event: {e}")
                        devices = find_keyboard_devices()  # Try to reconnect
            
        except Exception as e:
            logger.error(f"Error in evdev keyboard listener: {e}")