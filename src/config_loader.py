import os
from pathlib import Path


def find_config_file():
    """
    Find configuration file using XDG-compliant search order.
    
    Search order:
    1. ./config/default.json (current directory)
    2. ~/.config/daimonkms/config.json (XDG standard)
    
    Returns:
        Path object if config file found, None otherwise
    """
    # Check current directory first
    local_config = Path("config/default.json")
    if local_config.exists():
        return local_config
    
    # Check XDG config directory
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        xdg_config = Path(xdg_config_home) / "daimonkms" / "config.json"
    else:
        # Default to ~/.config if XDG_CONFIG_HOME not set
        xdg_config = Path.home() / ".config" / "daimonkms" / "config.json"
    
    if xdg_config.exists():
        return xdg_config
    
    # No config file found
    return None
