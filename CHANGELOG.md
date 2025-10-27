# Changelog

All notable changes to HyprSTT will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-27

### Fixed
- **Critical: Signal handling blocked by Qt event loop** - Added QTimer to wake up Qt event loop every 500ms, allowing Python signal handlers (SIGUSR1) to be processed correctly. This fixes the core STT toggle functionality.
- **Race condition in toggle notifications** - Removed state-based notifications from toggle-stt.sh to eliminate inverted notification messages. Python now handles all notifications correctly based on actual state changes.
- **Missing dependencies in installation scripts** - Added wl-clipboard and libsndfile to all installation scripts and documentation (install.sh, quick-setup.sh, README.md, CLAUDE.md).

### Added
- **Performance optimization** - Removed unnecessary scipy resampling (48kHz→16kHz) that was slowing down transcription. Whisper now handles resampling internally using its optimized implementation, resulting in 200-500ms+ faster transcription depending on recording length.
- **Testing infrastructure** - Added test-stt.sh automated test script for verifying STT functionality after changes.
- **Testing documentation** - Created comprehensive TESTING.md guide with manual testing procedures, common issues, and regression prevention guidelines.
- **CHANGELOG.md** - Added this changelog to track version history.

### Changed
- **audio_capture.py** - Now returns audio at native sample rate (44.1kHz/48kHz) instead of downsampling to 16kHz. Returns tuple (audio_data, sample_rate).
- **whisper_processor.py** - Accepts sample_rate parameter and writes WAV files at native rate instead of hardcoded 16kHz.
- **main.py** - Updated to handle new tuple return from stop_recording() and pass sample_rate to transcription.
- **quick-setup.sh** - Now uses `pip install -r requirements.txt` instead of hardcoded package list for consistency.
- **Dependencies documentation** - Expanded CLAUDE.md Dependencies & System Requirements section with categorized lists and explanations.

### Removed
- **scipy dependency** - Removed scipy.signal import from audio_capture.py as it's no longer needed for resampling.

## Version History

- **1.0.0** (2025-10-27) - First stable release with critical bug fixes and performance improvements

[1.0.0]: https://github.com/AcceleratedIndustries/HyprSTT/releases/tag/v1.0.0
