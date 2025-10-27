import os
import sys
import threading
import yaml
import signal
import time
import functools
from typing import Dict, Any, Optional, List, Tuple
import json
import subprocess
import warnings

# Suppress ALSA warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pyaudio")

# Local imports
from .audio_capture import AudioCapture
from .whisper_processor import WhisperProcessor
from .hyprland_manager import HyprlandManager
from .wayland_injector import WaylandInjector
from .keyboard_listener import KeyboardListener
from .utils import create_notification, get_config_path, setup_logger, check_dependencies
from PyQt6.QtWidgets import QApplication
from .tray_icon import TrayIcon

# Configure logger
logger = setup_logger("hyprstt")

class WhisperSTTController:
    """
    Main controller for HyprSTT system on Hyprland
    """
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
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "audio": {
                "rate": 16000,
                "chunk": 1024,
                "channels": 1
            },
            "whisper": {
                "model_size": "base",
                "device": "auto",
                "compute_type": "float16",
                "language": "en",
                "models_dir": os.path.expanduser("~/.cache/whisper")
            },
            "hotkeys": {
                "method": "external",
                "external_script": "./toggle-stt.sh",
                "toggle_recording": ["CTRL", "ALT", "SPACE"],
                "use_hypr_dispatch": False
            },
            "ui": {
                "notifications": True,
                "notification_timeout": 2
            }
        }
        
        config = default_config.copy()
        
        # If config path not provided, use default
        if not config_path:
            config_path = get_config_path()
            
        # Load config from file if it exists
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    
                if file_config:
                    # Update config recursively
                    self._update_dict_recursive(config, file_config)
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                
        return config
    
    def _update_dict_recursive(self, target: Dict, source: Dict):
        """
        Update dictionary recursively
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with updates
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value
                
    def _init_components(self):
        """Initialize system components"""
        try:
            # Check dependencies
            if not check_dependencies():
                logger.error("Missing system dependencies")
                return
                
            # Initialize components one by one with careful error handling
            try:
                # Initialize audio capture
                logger.info("Initializing audio capture...")
                self.audio_capture = AudioCapture(
                    rate=self.config["audio"]["rate"],
                    chunk=self.config["audio"]["chunk"],
                    channels=self.config["audio"]["channels"],
                    max_duration=self.config["audio"].get("max_duration", 0),
                    device_index=self.config["audio"].get("device_index"),
                    on_recording_change=self._on_recording_changed
                )
                logger.info("Audio capture initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize audio capture: {e}")
                raise
                
            try:
                # Initialize Whisper processor
                logger.info("Initializing Whisper processor...")
                self.whisper_processor = WhisperProcessor(
                    model_size=self.config["whisper"]["model_size"],
                    device=self.config["whisper"]["device"],
                    compute_type=self.config["whisper"]["compute_type"],
                    models_dir=self.config["whisper"]["models_dir"],
                    language=self.config["whisper"]["language"],
                    verbose=True
                )
                logger.info("Whisper processor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Whisper processor: {e}")
                raise
                
            try:
                # Initialize text injector
                logger.info("Initializing text injector...")
                self.text_injector = WaylandInjector()
                logger.info("Text injector initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize text injector: {e}")
                raise
            
            # Set up keyboard listener based on method
            hotkey_method = self.config["hotkeys"].get("method", "external")
            try:
                logger.info(f"Setting up keyboard listener (method: {hotkey_method})...")

                if hotkey_method == "external":
                    logger.info("Using external script method - no direct keyboard monitoring needed")
                    logger.info("Configure your compositor to call the toggle script for hotkey functionality")
                elif hotkey_method == "direct":
                    if self.config["hotkeys"]["use_hypr_dispatch"]:
                        self._setup_hyprland_listener()
                    else:
                        self._setup_direct_hotkey_listener()
                elif hotkey_method == "disabled":
                    logger.info("Hotkey method disabled - only external signals will work")
                else:
                    logger.warning(f"Unknown hotkey method '{hotkey_method}', falling back to external")

                logger.info("Keyboard listener setup successfully")
            except Exception as e:
                logger.error(f"Failed to setup keyboard listener: {e}")
                # Don't raise for external method as it's not critical
                if hotkey_method == "direct":
                    raise

            # Visual indicator has been removed from this version for reliability
            logger.info("Visual indicator disabled (removed for stability)")

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

            # Mark as initialized
            self.initialized = True
            logger.info("System initialized successfully")
            
        except Exception as e:
            import traceback
            logger.error(f"Error initializing components: {e}")
            logger.error(traceback.format_exc())
            self.initialized = False
            print(f"Error initializing: {e}. See log for details.")
    
    def _setup_hyprland_listener(self):
        """Set up Hyprland event listener for hotkeys"""
        try:
            # Save the configured hotkey combination
            self.toggle_combo = self.config["hotkeys"]["toggle_recording"]
            
            # Normalize hotkey format
            self.toggle_combo = [key.upper() for key in self.toggle_combo]
            
            # Format as Hyprland keybind string
            hotkey_str = ",".join(self.toggle_combo)
            
            # Start hyprland event listener
            self.keyboard_listener_thread = HyprlandManager.listen_for_events(
                self._handle_hyprland_event
            )
            
            if self.keyboard_listener_thread:
                logger.info(f"Hyprland event listener started for hotkey: {hotkey_str}")
            else:
                logger.warning("Failed to start Hyprland event listener, falling back to direct keyboard monitoring")
                self._setup_direct_hotkey_listener()
                
        except Exception as e:
            logger.error(f"Error setting up Hyprland listener: {e}")
            logger.warning("Falling back to direct keyboard monitoring")
            self._setup_direct_hotkey_listener()
    
    def _setup_direct_hotkey_listener(self):
        """Set up direct hotkey listener as fallback"""
        try:
            # Create keyboard listener
            keyboard_listener = KeyboardListener(
                callback=self._toggle_recording,
                keys=self.config["hotkeys"]["toggle_recording"]
            )
            
            # Start the listener
            self.keyboard_listener_thread = keyboard_listener.start()
            
            if self.keyboard_listener_thread:
                logger.info(f"Direct keyboard listener started with hotkey: {self.config['hotkeys']['toggle_recording']}")
            else:
                logger.error("Failed to start direct keyboard listener")
                
        except Exception as e:
            logger.error(f"Error setting up direct hotkey listener: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _handle_hyprland_event(self, event: str):
        """
        Handle Hyprland events
        
        Args:
            event: Event string from Hyprland
        """
        try:
            # Parse event
            if event.startswith("bindym>>"):
                # Keyboard shortcut event
                parts = event.split(">>")
                if len(parts) < 2:
                    return
                    
                keys_pressed = parts[1].strip()
                
                # Format hotkey string from config
                config_hotkey = ",".join(self.toggle_combo).lower()
                
                # Convert Hyprland key format to our format
                # Example: SUPER+SPACE -> super,space
                hypr_hotkey = keys_pressed.lower().replace("+", ",")
                
                # Check if this is our toggle shortcut
                if hypr_hotkey == config_hotkey:
                    logger.info(f"Detected hotkey: {keys_pressed}")
                    self._toggle_recording()
        except Exception as e:
            logger.error(f"Error handling Hyprland event: {e}")

    def _write_state(self, state: str):
        """Write current state to file for external script notifications"""
        try:
            with open(self.state_file, 'w') as f:
                f.write(state)
        except Exception as e:
            logger.warning(f"Failed to write state file: {e}")

    def _on_recording_changed(self, is_recording: bool):
        """
        Callback for recording state changes

        Args:
            is_recording: New recording state
        """
        logger.info(f"*** DEBUGGING: Recording state changed from {self.is_recording} to {is_recording}")
        self.is_recording = is_recording

        # Write state for external script
        self._write_state("recording" if is_recording else "idle")

        # Visual indicator has been removed for stability

        if self.config["ui"]["notifications"]:
            if is_recording:
                create_notification(
                    "HyprSTT",
                    "Recording started...",
                    timeout=self.config["ui"]["notification_timeout"]
                )
            else:
                create_notification(
                    "HyprSTT",
                    "Processing speech...",
                    timeout=self.config["ui"]["notification_timeout"]
                )

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

    def _toggle_recording(self):
        """Toggle recording state"""
        logger.info(f"*** DEBUGGING: _toggle_recording called - is_recording={self.is_recording}, initialized={self.initialized}")
        
        if not self.initialized:
            logger.error("*** DEBUGGING: System not initialized")
            return

        # Add debouncing to prevent rapid toggle calls
        current_time = time.time()
        if hasattr(self, '_last_toggle_time'):
            time_since_last = current_time - self._last_toggle_time
            if time_since_last < 0.5:  # Ignore toggles within 500ms
                logger.warning(f"*** DEBUGGING: Ignoring rapid toggle (time since last: {time_since_last:.3f}s)")
                return
        self._last_toggle_time = current_time

        if self.is_recording:
            logger.info("*** DEBUGGING: Currently recording, stopping...")
            # Stop recording
            audio_data = self.audio_capture.stop_recording()
            logger.info(f"*** DEBUGGING: Got audio data: {audio_data is not None}")

            if audio_data is not None:
                # Generate a unique ID for this transcription attempt
                transcription_id = int(time.time())
                logger.info(f"*** DEBUGGING: Starting transcription #{transcription_id} in background thread")


                # Process in background to avoid blocking UI
                threading.Thread(
                    target=self._process_audio,
                    args=(audio_data, transcription_id),
                    daemon=True
                ).start()
            else:
                logger.warning("*** DEBUGGING: No audio data captured, skipping transcription")
        else:
            logger.info("*** DEBUGGING: Not recording, starting new recording...")
            # Start recording
            self.audio_capture.start_recording()
            logger.info("*** DEBUGGING: Called audio_capture.start_recording()")
    
    def _process_audio(self, audio_data, transcription_id=None):
        """
        Process recorded audio and inject transcribed text
        
        Args:
            audio_data: Audio data to process
        """
        try:
            # Get focused window before processing starts (optional for non-Hyprland compositors)
            window_info = HyprlandManager.get_focused_window()
            
            if not window_info:
                logger.warning("Could not get focused window (likely not running under Hyprland)")
                # Continue processing anyway for non-Hyprland compositors
            else:
                # Check if window accepts text input (only if we have window info)
                if not HyprlandManager.is_text_input(window_info):
                    logger.warning(f"Window may not accept text input: {window_info}")
                
            # Transcribe audio
            id_info = f" #{transcription_id}" if transcription_id else ""
            logger.info(f"Transcribing audio{id_info}...")
            transcribed_text = self.whisper_processor.transcribe_audio(audio_data)
            
            if not transcribed_text:
                logger.error("Transcription failed or returned empty text")
                if self.config["ui"]["notifications"]:
                    # Save recorded audio for debugging if transcription fails
                    debug_dir = os.path.expanduser("~/.local/share/hyprstt/debug")
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_file = os.path.join(debug_dir, f"failed_audio_{transcription_id or int(time.time())}.wav")

                    try:
                        # Try to save the audio for debugging
                        self.audio_capture.save_to_file(debug_file)
                        logger.info(f"Saved failed audio to {debug_file} for debugging")
                    except Exception as e:
                        logger.error(f"Could not save debug audio: {e}")

                    # Check if we have a microphone permission or setup issue
                    try:
                        # Get last audio level to check if we're getting zero audio
                        if hasattr(self.audio_capture, 'last_audio_level') and self.audio_capture.last_audio_level == 0.0:
                            message = "NO AUDIO DETECTED! Microphone not working or not capturing any sound. Check device settings."
                            logger.error("Audio level is exactly 0.00 - Microphone likely not working at all")
                        else:
                            # Run a quick test to check microphone status
                            import subprocess
                            mic_info = subprocess.run(["pactl", "list", "sources"], check=True, capture_output=True, text=True).stdout
                            if "input" in mic_info.lower() and "running" not in mic_info.lower():
                                message = "Microphone may not be properly configured. Check audio input settings."
                            else:
                                message = "Transcription failed or no speech detected. Try speaking longer and clearer."
                    except Exception as e:
                        # Unable to check further, give a generic message
                        logger.error(f"Error checking microphone: {e}")
                        message = "Transcription failed or no speech detected. Try speaking longer and clearer."

                    create_notification(
                        "HyprSTT",
                        message,
                        timeout=self.config["ui"]["notification_timeout"]
                    )
                return
                
            # Log the transcribed text
            id_info = f" #{transcription_id}" if transcription_id else ""
            logger.info(f"Transcribed text{id_info}: {transcribed_text}")
            
            # Copy text to clipboard and show notification
            logger.info(f"Copying transcribed text to clipboard")
            self.text_injector.inject_text(transcribed_text, delay=0.1)
            logger.info(f"Text copied to clipboard, notification sent")
            
            # Show notification with transcribed text
            if self.config["ui"]["notifications"]:
                # Check if audio level was suspiciously low but still gave a result
                if hasattr(self.audio_capture, 'last_audio_level') and self.audio_capture.last_audio_level < 10.0:
                    preview = (transcribed_text[:40] + "...") if len(transcribed_text) > 40 else transcribed_text
                    create_notification(
                        "HyprSTT",
                        f"Transcribed (low audio level!): {preview}",
                        timeout=self.config["ui"]["notification_timeout"] * 2  # Show result notification longer
                    )
                else:
                    preview = (transcribed_text[:40] + "...") if len(transcribed_text) > 40 else transcribed_text
                    create_notification(
                        "HyprSTT",
                        f"Transcribed: {preview}",
                        timeout=self.config["ui"]["notification_timeout"] * 2  # Show result notification longer
                    )
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            if self.config["ui"]["notifications"]:
                create_notification(
                    "HyprSTT",
                    f"Error processing audio: {str(e)}",
                    timeout=self.config["ui"]["notification_timeout"]
                )
    
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
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop recording if active
            if self.audio_capture and self.is_recording:
                self.audio_capture.stop_recording()

            # Clean up audio capture
            if self.audio_capture:
                self.audio_capture.cleanup()

            # Visual indicator cleanup no longer needed

            # Hide tray icon
            if self.tray_icon:
                self.tray_icon.hide()

            logger.info("System shutdown complete")
            return True
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False

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
    
if __name__ == "__main__":
    main()