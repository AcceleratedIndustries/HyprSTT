import os
import logging
import subprocess
import json
from typing import Optional, List

def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.expanduser("~/.local/share/hyprstt/logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, f"{name}.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

def get_config_path() -> str:
    """
    Get the path to the configuration file
    
    Returns:
        Path to configuration file
    """
    # Check XDG_CONFIG_HOME first
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        config_dir = os.path.join(xdg_config, "hyprstt")
    else:
        # Fall back to ~/.config
        config_dir = os.path.expanduser("~/.config/hyprstt")
    
    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    return os.path.join(config_dir, "config.yml")

def create_notification(title: str, message: str, timeout: int = 5):
    """
    Create a desktop notification compatible with Wayland
    
    Args:
        title: Notification title
        message: Notification message
        timeout: Notification timeout in seconds
    """
    try:
        # Try using notify-send first (works with most notification daemons)
        # Suppress stderr to avoid GDBus error messages when notification daemon is unavailable
        subprocess.run(
            ["notify-send", "-t", str(timeout * 1000), title, message],
            check=True,
            stderr=subprocess.DEVNULL
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            # Fall back to using the Wayland-native mako notifications
            subprocess.Popen(
                ["makoctl", "set-urgent"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.Popen(
                ["echo", f"{title}: {message}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            # Both methods failed, just print to console
            print(f"Notification: {title}: {message}")

def check_dependencies() -> bool:
    """
    Check if required system dependencies are installed
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    wayland_dependencies = ["wtype", "socat"]
    missing = []
    
    for dep in wayland_dependencies:
        try:
            subprocess.run(["which", dep], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            missing.append(dep)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install them using your package manager.")
        print("For Arch-based distributions:")
        print(f"  sudo pacman -S {' '.join(missing)}")
        print("For other distributions, you may need to compile them from source.")
        return False
    
    # Check compositor and warn about features
    compositor = check_wayland_compositor()
    if compositor == "hyprland":
        pass  # All features supported
    elif compositor in ["niri", "sway", "kwin", "wayfire"]:
        print(f"Running under {compositor}. Some Hyprland-specific features may not work.")
    elif compositor == "unknown_wayland":
        print("Running under unknown Wayland compositor. Some features may not work.")
    elif compositor == "not_wayland":
        print("Warning: Not running under Wayland. Most features may not work.")
    
    return True

def is_torch_available() -> bool:
    """
    Check if PyTorch is installed and available
    
    Returns:
        True if PyTorch is available, False otherwise
    """
    try:
        import torch
        return True
    except ImportError:
        return False

def is_cuda_available() -> bool:
    """
    Check if CUDA is available for PyTorch
    
    Returns:
        True if CUDA is available, False otherwise
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def get_audio_devices() -> list:
    """
    Get list of available audio input devices
    
    Returns:
        List of audio input devices
    """
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        devices = []
        
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                devices.append({
                    "index": i,
                    "name": device_info["name"],
                    "channels": device_info["maxInputChannels"],
                    "sample_rate": int(device_info["defaultSampleRate"])
                })
        
        p.terminate()
        return devices
    except ImportError:
        return []

def is_hyprland_active() -> bool:
    """
    Check if Hyprland is the current compositor
    
    Returns:
        True if Hyprland is active, False otherwise
    """
    # Check environment variables
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and os.environ.get("XDG_SESSION_TYPE") == "wayland":
        return True
    
    # Check running processes as fallback
    try:
        output = subprocess.check_output(["ps", "aux"], universal_newlines=True)
        return "Hyprland" in output
    except subprocess.SubprocessError:
        return False

def get_hyprland_version() -> Optional[str]:
    """
    Get Hyprland version
    
    Returns:
        Hyprland version string or None if not found
    """
    try:
        output = subprocess.check_output(["hyprctl", "version"], universal_newlines=True)
        for line in output.splitlines():
            if line.startswith("Hyprland"):
                return line.split("Hyprland")[1].strip()
        return None
    except subprocess.SubprocessError:
        return None

def get_active_hyprland_monitors() -> List[dict]:
    """
    Get list of active Hyprland monitors
    
    Returns:
        List of monitor information dictionaries
    """
    try:
        output = subprocess.check_output(["hyprctl", "monitors", "-j"], universal_newlines=True)
        monitors = json.loads(output)
        
        return [{
            "name": monitor.get("name"),
            "description": monitor.get("description"),
            "width": monitor.get("width"),
            "height": monitor.get("height"),
            "refresh_rate": monitor.get("refreshRate"),
            "x": monitor.get("x"),
            "y": monitor.get("y"),
            "active": monitor.get("focused", False)
        } for monitor in monitors]
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return []

def check_wayland_compositor() -> str:
    """
    Check which Wayland compositor is running
    
    Returns:
        Name of the Wayland compositor or "unknown"
    """
    # Check if Hyprland is running
    if is_hyprland_active():
        return "hyprland"
    
    # Check for other common Wayland compositors
    if os.environ.get("SWAYSOCK"):
        return "sway"
    
    if os.environ.get("_MUTTER_PRESENTATION_TIME"):
        return "mutter"
    
    try:
        output = subprocess.check_output(["ps", "aux"], universal_newlines=True)
        if "kwin_wayland" in output:
            return "kwin"
        if "wayfire" in output:
            return "wayfire"
        if "niri" in output:
            return "niri"
    except subprocess.SubprocessError:
        pass
    
    # Check if we're running in Wayland at all
    if os.environ.get("WAYLAND_DISPLAY"):
        return "unknown_wayland"
    
    return "not_wayland"