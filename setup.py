from setuptools import setup, find_packages

setup(
    name="hyprstt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "PyAudio>=0.2.11",
        "sounddevice>=0.4.1",
        "soundfile>=0.10.3.post1",
        "torch>=1.13.0",
        "torchaudio>=0.13.0",
        "faster-whisper>=0.5.0",
        "PyYAML>=6.0",
        "evdev>=1.6.0",
    ],
    entry_points={
        'console_scripts': [
            'hyprstt=src.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Speech-to-Text system for Hyprland/Wayland using Whisper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hyprstt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
)