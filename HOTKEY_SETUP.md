# HyprSTT Hotkey Setup Guide

This guide explains how to configure hotkeys for HyprSTT across different Wayland compositors.

## Overview

HyprSTT supports multiple hotkey methods:

1. **External Script (Recommended)** - Configure compositor hotkeys to call the toggle script
2. **Direct Monitoring** - Application-level hotkey detection (limited functionality)
3. **Disabled** - Only external signals work (SIGUSR1)

## Quick Setup (External Script Method)

The external script method is the most reliable and works across all Wayland compositors.

### 1. Configure HyprSTT

Ensure your `~/.config/hyprstt/config.yml` has:

```yaml
hotkeys:
  method: "external"
  external_script: "./toggle-stt.sh"
```

### 2. Configure Your Compositor

Choose your compositor below and add the appropriate configuration:

---

## Hyprland Configuration

Add to your `~/.config/hypr/hyprland.conf`:

```conf
# HyprSTT toggle hotkey
bind = SUPER, F9, exec, /home/[username]/claude-stt/hyprstt/toggle-stt.sh

# Alternative key combinations:
# bind = SUPER SHIFT, SPACE, exec, /home/[username]/claude-stt/hyprstt/toggle-stt.sh
# bind = CTRL ALT, S, exec, /home/[username]/claude-stt/hyprstt/toggle-stt.sh
```

Replace `[username]` with your actual username or use the full path to the script.

To reload Hyprland config: `hyprctl reload`

---

## Niri Configuration

Add to your `~/.config/niri/config.kdl`:

```kdl
binds {
    // HyprSTT toggle
    "Mod+F9" = { spawn = ["/home/[username]/claude-stt/hyprstt/toggle-stt.sh"]; };

    // Alternative combinations:
    // "Mod+Shift+Space" = { spawn = ["/home/[username]/claude-stt/hyprstt/toggle-stt.sh"]; };
    // "Ctrl+Alt+S" = { spawn = ["/home/[username]/claude-stt/hyprstt/toggle-stt.sh"]; };
}
```

Replace `[username]` with your actual username.

To reload Niri config: `niri msg action validate-config && systemctl --user reload niri`

---

## Sway Configuration

Add to your `~/.config/sway/config`:

```conf
# HyprSTT toggle hotkey
bindsym $mod+F9 exec /home/[username]/claude-stt/hyprstt/toggle-stt.sh

# Alternative key combinations:
# bindsym $mod+Shift+space exec /home/[username]/claude-stt/hyprstt/toggle-stt.sh
# bindsym Ctrl+Alt+s exec /home/[username]/claude-stt/hyprstt/toggle-stt.sh
```

Replace `[username]` with your actual username.

To reload Sway config: `swaymsg reload`

---

## River Configuration

Add to your `~/.config/river/init`:

```bash
# HyprSTT toggle hotkey
riverctl map normal Super F9 spawn "/home/[username]/claude-stt/hyprstt/toggle-stt.sh"

# Alternative key combinations:
# riverctl map normal Super+Shift space spawn "/home/[username]/claude-stt/hyprstt/toggle-stt.sh"
# riverctl map normal Control+Alt s spawn "/home/[username]/claude-stt/hyprstt/toggle-stt.sh"
```

Replace `[username]` with your actual username.

---

## Alternative: Direct Monitoring Method

If you prefer application-level hotkey detection, configure:

```yaml
hotkeys:
  method: "direct"
  toggle_recording: ["CTRL", "ALT", "SPACE"]  # Avoid function keys
  use_hypr_dispatch: false  # Use direct keyboard monitoring
```

**Limitations:**
- Requires keyboard permissions
- May not work with all key combinations
- Function keys often don't work due to compositor conflicts
- Less reliable than external script method

---

## Installation Tips

### 1. Make Script Executable

```bash
chmod +x /path/to/hyprstt/toggle-stt.sh
```

### 2. Use Absolute Paths

Always use the full absolute path to the toggle script in your compositor config to avoid path resolution issues.

### 3. Test the Setup

1. Start HyprSTT: `cd hyprstt && ./run-dev.sh`
2. Test the hotkey you configured
3. You should see a notification and visual indicator

### 4. Recommended Key Combinations

Good choices that typically don't conflict:
- `Super + F9` (if F9 isn't bound)
- `Super + Shift + Space`
- `Ctrl + Alt + S`
- `Super + Ctrl + Space`

Avoid:
- Function keys (F1-F12) without modifiers
- Common shortcuts like `Ctrl+C`, `Alt+Tab`, etc.
- Keys used by your terminal or applications

---

## Troubleshooting

### Script Not Found
- Ensure the path to `toggle-stt.sh` is absolute and correct
- Check that the script is executable: `ls -l toggle-stt.sh`

### No Response to Hotkey
- Check that HyprSTT is running: `ps aux | grep "python -m src.main"`
- Test the script manually: `./toggle-stt.sh`
- Check compositor logs for binding errors

### Permission Errors
- Ensure the script has execute permissions
- Check file ownership and accessibility

### Notifications Not Showing
- Ensure `notify-send` is installed
- Check that notification daemon is running
- Test manually: `notify-send "Test" "Message"`

---

## Advanced Configuration

### Custom Script Location

You can move the toggle script to a standard location:

```bash
# Copy to user bin directory
cp toggle-stt.sh ~/.local/bin/hyprstt-toggle
chmod +x ~/.local/bin/hyprstt-toggle

# Update compositor config to use:
# ~/.local/bin/hyprstt-toggle
```

### Multiple Instances

The script handles multiple HyprSTT instances automatically, using the first one found and displaying a warning.

### State-based Notifications

The script reads the state file at `~/.local/share/hyprstt/state` to provide context-aware notifications showing whether recording started or stopped.