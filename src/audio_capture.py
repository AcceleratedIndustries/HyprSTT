import pyaudio
import wave
import threading
import numpy as np
import time
import logging
import os
import sys
from typing import Optional, Callable

# Configure logger
logger = logging.getLogger("whisper_stt")

class AudioCapture:
    def __init__(self,
                 rate: int = 16000,
                 chunk: int = 1024,
                 channels: int = 1,
                 max_duration: int = 0,
                 device_index: Optional[int] = None,
                 on_recording_change: Optional[Callable[[bool], None]] = None):
        """
        Initialize audio capture module

        Args:
            rate: Sample rate (Whisper expects 16kHz)
            chunk: Buffer size
            channels: Number of audio channels (1 for mono)
            max_duration: Maximum recording duration in seconds (0 for unlimited)
            device_index: PyAudio device index (None for default)
            on_recording_change: Callback for recording state changes
        """
        self.target_rate = rate  # Target rate for Whisper (16kHz)
        self.chunk = chunk
        self.channels = channels
        self.format = pyaudio.paInt16
        self.device_index = device_index

        # Suppress ALSA warnings during PyAudio initialization
        stderr_fd = os.dup(2)
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), 2)
            try:
                self.p = pyaudio.PyAudio()
            finally:
                os.dup2(stderr_fd, 2)
                os.close(stderr_fd)

        # Determine actual recording rate based on device capabilities
        self.rate = self._get_device_sample_rate()
        logger.info(f"Device sample rate: {self.rate} Hz, target rate: {self.target_rate} Hz")

        self.recording = False
        self.frames = []
        self.recording_thread = None
        self.on_recording_change = on_recording_change
        self.max_duration = max_duration  # Maximum recording duration in seconds (0 for no limit)
        self.last_audio_level = 0.0  # Track audio level to help diagnose issues

    def _get_device_sample_rate(self) -> int:
        """Get the native sample rate for the recording device"""
        if self.device_index is not None:
            try:
                info = self.p.get_device_info_by_index(self.device_index)
                return int(info['defaultSampleRate'])
            except Exception as e:
                logger.warning(f"Could not get device sample rate, using target rate: {e}")
                return self.target_rate
        else:
            return self.target_rate

    def start_recording(self):
        """Start audio recording in a background thread"""
        if self.recording:
            logger.warning("*** DEBUGGING: Recording already in progress, ignoring start_recording call")
            return

        # Explicitly clear frames array to prevent memory leaks or old data retention
        self.frames = []
        logger.info("*** DEBUGGING: Starting new recording, frames buffer cleared")

        self.recording = True

        if self.on_recording_change:
            self.on_recording_change(True)

        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop audio recording and return the captured audio data"""
        if not self.recording:
            logger.warning("*** DEBUGGING: stop_recording called but not currently recording")
            return None

        logger.info("*** DEBUGGING: Stopping recording...")
        self.recording = False

        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)

        if self.on_recording_change:
            self.on_recording_change(False)

        if not self.frames:
            logger.warning("No audio frames were recorded")
            return None

        # Log frame information
        logger.info(f"Recorded {len(self.frames)} audio frames")

        # Check if we have enough data (at least 0.5 seconds)
        min_frames = int(0.5 * self.rate / self.chunk)
        if len(self.frames) < min_frames:
            logger.warning(f"Recording too short: {len(self.frames)} frames, minimum recommended is {min_frames}")
            # If too short, artificially pad with silence to help Whisper
            silence_chunk = np.zeros(self.chunk, dtype=np.int16).tobytes()
            padding_needed = min_frames - len(self.frames)
            logger.info(f"Adding {padding_needed} frames of silence padding")
            self.frames.extend([silence_chunk] * padding_needed)

        # Return audio data as numpy array
        try:
            audio_data = np.concatenate([np.frombuffer(frame, dtype=np.int16)
                                        for frame in self.frames])
            logger.info(f"Audio data shape: {audio_data.shape}, duration: {len(audio_data)/self.rate:.2f} seconds")
            logger.info(f"Audio sample rate: {self.rate} Hz (Whisper will resample to 16kHz internally)")

            # Analyze audio levels
            audio_level = np.abs(audio_data).mean()
            self.last_audio_level = audio_level  # Store for diagnostic use
            logger.info(f"Average audio level: {audio_level:.2f}")

            # Warn if audio seems to be silence or very quiet
            # Adjusted thresholds for high-quality USB mics like Yeti X
            if audio_level < 500:  # Increased threshold for USB mics that have higher gain
                logger.warning("Audio recording appears to be very quiet or silence")
                # If audio is essentially silent, don't even try to transcribe
                if audio_level < 50:  # Higher threshold for USB mics
                    logger.error("Audio recording is completely silent, skipping transcription")
                    return None
                
            # If audio level is exactly 0.0, that's a sign of a microphone problem
            if audio_level == 0.0:
                logger.error("CRITICAL: Audio level is exactly 0.0 - Microphone may not be working!")
                # Try to get device info to help diagnose
                try:
                    info = self.p.get_default_input_device_info()
                    logger.error(f"Default input device: {info['name']} (index: {info['index']})")
                except Exception as e:
                    logger.error(f"Could not get input device info: {e}")

            return (audio_data, self.rate)
        except Exception as e:
            logger.error(f"Error processing audio frames: {e}")
            return None
    
    def _record_audio(self):
        """Internal method for recording audio"""
        try:
            # Check if we can get input devices before trying to record
            info = self.p.get_default_input_device_info()
            logger.info(f"Using input device: {info['name']} (index: {info['index']})")
            
            # Add a debug message to help identify microphone issues
            device_count = self.p.get_device_count()
            input_devices = []
            for i in range(device_count):
                dev_info = self.p.get_device_info_by_index(i)
                if dev_info['maxInputChannels'] > 0:
                    input_devices.append(f"{dev_info['name']} (index: {i})")
            
            if input_devices:
                logger.info(f"Available input devices: {', '.join(input_devices)}")
            else:
                logger.error("No input devices found! This is likely the cause of silent recordings.")
        except Exception as e:
            logger.error(f"Error checking audio devices: {e}")
            
        # Open stream with optional device selection
        stream_params = {
            'format': self.format,
            'channels': self.channels,
            'rate': self.rate,
            'input': True,
            'frames_per_buffer': self.chunk
        }

        if self.device_index is not None:
            stream_params['input_device_index'] = self.device_index
            logger.info(f"Using audio device index: {self.device_index}")

        stream = self.p.open(**stream_params)

        start_time = time.time()
        max_frames = 0

        # Calculate max frames if max_duration is set
        if self.max_duration > 0:
            max_frames = int((self.rate * self.max_duration) / self.chunk)

        while self.recording:
            try:
                # If max_duration reached, automatically stop recording
                if self.max_duration > 0 and time.time() - start_time > self.max_duration:
                    print(f"Max recording duration of {self.max_duration}s reached, stopping")
                    self.recording = False
                    break

                # If max frames reached, automatically stop recording
                if max_frames > 0 and len(self.frames) >= max_frames:
                    print(f"Max frames ({max_frames}) reached, stopping")
                    self.recording = False
                    break

                data = stream.read(self.chunk)
                self.frames.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break

        stream.stop_stream()
        stream.close()
    
    def save_to_file(self, filename: str):
        """Save recorded audio to WAV file"""
        if not self.frames:
            return False
            
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_recording()
        self.p.terminate()