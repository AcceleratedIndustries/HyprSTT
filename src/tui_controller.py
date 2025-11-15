"""
TUI-enhanced controller for HyprSTT
Integrates the Textual TUI with the WhisperSTTController
"""
import os
import sys
import threading
import signal
from typing import Optional

from .main import WhisperSTTController
from .tui import HyprSTTTUI
from .utils import setup_logger

logger = setup_logger("hyprstt.tui_controller")


class TUIWhisperSTTController(WhisperSTTController):
    """
    Extended controller with TUI support
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the TUI controller

        Args:
            config_path: Path to configuration file
        """
        # Initialize without Qt app (TUI will handle the UI)
        super().__init__(config_path=config_path, qt_app=None)
        self.tui_app = None
        self._original_process_audio = None

    def _on_transcription_complete(self, text: str):
        """
        Callback when transcription completes

        Args:
            text: Transcribed text
        """
        if self.tui_app:
            # Update TUI with new transcription
            self.tui_app.call_from_thread(
                self.tui_app.on_transcription_complete,
                text
            )

    def _process_audio(self, audio_data, sample_rate, transcription_id=None):
        """
        Override to hook into transcription completion

        Args:
            audio_data: Audio data to process
            sample_rate: Sample rate of the audio data
            transcription_id: Optional ID for tracking this transcription
        """
        # Call parent implementation
        super()._process_audio(audio_data, sample_rate, transcription_id)

        # If we successfully transcribed, get the text and notify TUI
        # We can check the logs or add a callback mechanism
        # For now, we'll use a simple approach: check if text was injected

    def run_with_tui(self):
        """Run the controller with TUI interface"""
        if not self.initialized:
            logger.error("System not initialized")
            return False

        logger.info("Starting HyprSTT with TUI interface")

        # Create TUI app
        self.tui_app = HyprSTTTUI(controller=self)

        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.cleanup()
            if self.tui_app:
                self.tui_app.exit()
            sys.exit(0)

        def toggle_handler(sig, frame):
            logger.info("Toggle signal received")
            self._toggle_recording()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGUSR1, toggle_handler)

        # Monkey-patch _process_audio to capture transcriptions
        original_process_audio = super()._process_audio

        def wrapped_process_audio(audio_data, sample_rate, transcription_id=None):
            # Import here to avoid circular dependency
            from .whisper_processor import WhisperProcessor

            try:
                # Get focused window before processing starts (optional for non-Hyprland compositors)
                from .hyprland_manager import HyprlandManager
                window_info = HyprlandManager.get_focused_window()

                # Transcribe audio
                logger.info(f"Transcribing audio...")
                transcribed_text = self.whisper_processor.transcribe_audio(audio_data, sample_rate=sample_rate)

                if transcribed_text:
                    # Notify TUI
                    self._on_transcription_complete(transcribed_text)

                    # Log the transcribed text
                    logger.info(f"Transcribed text: {transcribed_text}")

                    # Copy text to clipboard and show notification
                    logger.info(f"Copying transcribed text to clipboard")
                    self.text_injector.inject_text(transcribed_text, delay=0.1)

                    # Show notification if enabled
                    if self.config["ui"]["notifications"]:
                        from .utils import create_notification
                        preview = (transcribed_text[:40] + "...") if len(transcribed_text) > 40 else transcribed_text
                        create_notification(
                            "HyprSTT",
                            f"Transcribed: {preview}",
                            timeout=self.config["ui"]["notification_timeout"] * 2
                        )
                else:
                    logger.error("Transcription failed or returned empty text")
                    if self.config["ui"]["notifications"]:
                        from .utils import create_notification
                        create_notification(
                            "HyprSTT",
                            "Transcription failed or no speech detected",
                            timeout=self.config["ui"]["notification_timeout"]
                        )

            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                if self.config["ui"]["notifications"]:
                    from .utils import create_notification
                    create_notification(
                        "HyprSTT",
                        f"Error processing audio: {str(e)}",
                        timeout=self.config["ui"]["notification_timeout"]
                    )

        self._process_audio = wrapped_process_audio

        try:
            # Run TUI (this blocks until the app exits)
            return self.tui_app.run() is None  # Textual's run() returns None on success
        except Exception as e:
            logger.error(f"Error running TUI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point for TUI mode"""
    controller = TUIWhisperSTTController()

    # Run with TUI
    success = controller.run_with_tui()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
