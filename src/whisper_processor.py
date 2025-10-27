import os
import numpy as np
from typing import Optional, Dict, Any, Union
import torch
import logging

# Configure logger
logger = logging.getLogger("whisper_stt")

# Use faster-whisper if available, fall back to official implementation
try:
    from faster_whisper import WhisperModel
    USING_FASTER_WHISPER = True
except ImportError:
    import whisper
    USING_FASTER_WHISPER = False
    
# Fix path for model dir
def expand_path(path):
    """Expand user home directory and make sure the path exists"""
    if not path:
        return None
    expanded = os.path.expanduser(path)
    os.makedirs(expanded, exist_ok=True)
    return expanded

class WhisperProcessor:
    def __init__(self, 
                 model_size: str = "base",
                 device: str = "auto",
                 compute_type: str = "float16",
                 models_dir: Optional[str] = None,
                 language: str = "en",
                 verbose: bool = False):
        """
        Initialize Whisper processor
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run model on ("cpu", "cuda", "auto")
            compute_type: Compute type for faster-whisper ("float16", "float32", "int8")
            models_dir: Directory to store/load models
            language: Language code for transcription
            verbose: Whether to print verbose output
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.models_dir = expand_path(models_dir)
        self.language = language
        self.verbose = verbose
        self.model = None
        self.last_audio_level = 0  # Track audio level to help filter false positives

        self._load_model()
        
    def _load_model(self):
        """Load the Whisper model"""
        if self.verbose:
            print(f"Loading Whisper {self.model_size} model...")
            
        try:
            if USING_FASTER_WHISPER:
                # Use faster-whisper implementation
                if self.device == "auto":
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                    
                # Create a temporary directory if models_dir is not set or has issues
                if not self.models_dir:
                    import tempfile
                    self.models_dir = os.path.join(tempfile.gettempdir(), "whisper-models")
                    os.makedirs(self.models_dir, exist_ok=True)
                    if self.verbose:
                        print(f"Using temporary directory for models: {self.models_dir}")
                
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=self.models_dir
                )
                
                if self.verbose:
                    print(f"Loaded faster-whisper model on {self.device}")
            else:
                # Use official OpenAI implementation
                if self.device == "auto":
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                    
                self.model = whisper.load_model(
                    self.model_size,
                    device=self.device,
                    download_root=self.models_dir
                )
                
                if self.verbose:
                    print(f"Loaded official whisper model on {self.device}")
        except Exception as e:
            import traceback
            print(f"Error loading Whisper model: {e}")
            print(traceback.format_exc())
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe_audio(self,
                        audio_data: Union[str, np.ndarray],
                        sample_rate: int = 16000,
                        options: Optional[Dict[str, Any]] = None) -> str:
        """
        Transcribe audio data to text

        Args:
            audio_data: Audio data as numpy array or path to audio file
            sample_rate: Sample rate of the audio data (Whisper resamples to 16kHz internally)
            options: Additional options for transcription

        Returns:
            Transcribed text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
            
        default_options = {
            "language": self.language,
            "task": "transcribe"
        }
        
        if options:
            default_options.update(options)
            
        try:
            # Log audio info for debugging
            if isinstance(audio_data, np.ndarray):
                logger.info(f"Audio data shape: {audio_data.shape}, dtype: {audio_data.dtype}, min: {audio_data.min()}, max: {audio_data.max()}")
                # Check if audio has content or is just silence
                audio_level = np.abs(audio_data).mean()
                self.last_audio_level = audio_level  # Store for false positive detection
                logger.info(f"Average audio level: {audio_level}")
                
                # Check if this is actually empty/zero audio
                if audio_level == 0.0:
                    logger.error("Audio data is completely zero - microphone not working or not recording!")
                    return ""
                
                # Adjusted thresholds for high-quality USB mics like Yeti X
                if audio_level < 200:  # Higher threshold for USB mics
                    logger.warning("Audio appears to be silence or very quiet")
                    # Don't even attempt to transcribe completely silent audio
                    if audio_level < 30:  # Higher threshold for USB mics
                        logger.error("Audio is completely silent, skipping transcription")
                        return ""
            else:
                logger.info(f"Audio data provided as file path: {audio_data}")

            if USING_FASTER_WHISPER:
                # Handle audio data based on type
                if isinstance(audio_data, str):
                    # File path provided
                    logger.info(f"Transcribing from file: {audio_data}")
                    segments, info = self.model.transcribe(
                        audio_data,
                        language=default_options["language"],
                        task=default_options["task"]
                    )
                    result = " ".join([segment.text for segment in segments])
                    logger.info(f"Transcription complete, found {len(list(segments))} segments")
                else:
                    # Convert numpy array to path (faster-whisper expects file path)
                    import tempfile
                    import soundfile as sf

                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        temp_path = f.name

                    logger.info(f"Saving audio to temporary file: {temp_path}")
                    try:
                        normalized_audio = audio_data.astype(np.float32) / 32768.0
                        sf.write(temp_path, normalized_audio, sample_rate)
                        logger.info(f"Temporary WAV file created at {sample_rate} Hz, size: {os.path.getsize(temp_path)} bytes")

                        segments, info = self.model.transcribe(
                            temp_path,
                            language=default_options["language"],
                            task=default_options["task"]
                        )
                        segment_list = list(segments)
                        result = " ".join([segment.text for segment in segment_list])
                        logger.info(f"Transcription complete, found {len(segment_list)} segments")
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            logger.info("Temporary WAV file deleted")
            else:
                # Use official OpenAI implementation
                if isinstance(audio_data, str):
                    # Load audio from file
                    audio_data = whisper.load_audio(audio_data)
                
                # Make sure audio is properly scaled
                if audio_data.dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                
                # Prepare audio for model
                audio_data = whisper.pad_or_trim(audio_data)
                
                # Transcribe
                result = self.model.transcribe(
                    audio_data,
                    language=default_options["language"],
                    task=default_options["task"]
                )
                
                return result["text"].strip()
                
            result = result.strip()
            logger.info(f"Raw transcription result: '{result}'")

            logger.info(f"Raw transcription result: '{result}'")
            
            # false_positives = [
            #     "thank you", "thanks", "thank you for watching",
            #     "you're welcome", "thanks for watching", 
            #     "please subscribe", "like and subscribe",
            #     "goodbye", "thank you for listening",
            #     "you", "you are", "you're", "You", "You are", "You're"  # Common outputs for silence
            # ]
            #
            # # Check if result is a likely false positive (case insensitive)
            # result_lower = result.lower()
            # if result and any(fp.lower() == result_lower for fp in false_positives):
            #     logger.warning(f"Detected potential false positive result: '{result}'")
            #     # If we suspect a false positive, check audio level before rejecting
            #     # This helps ensure we don't filter out legitimate instances of these phrases
            #     # Adjusted threshold for USB mics like Yeti X that have higher baseline levels
            #     if hasattr(self, 'last_audio_level') and self.last_audio_level < 150:  # Higher threshold for USB mics
            #         logger.warning("Audio level was very low, treating as false positive and rejecting result")
            #         return ""
            #     else:
            #         logger.info("Audio level was sufficient, keeping suspected false positive result")

            logger.info(f"Final transcription result: '{result}'")
            return result

        except Exception as e:
            import traceback
            logger.error(f"Error transcribing audio: {e}")
            logger.error(traceback.format_exc())
            return ""