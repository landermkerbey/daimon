import json
from pathlib import Path


class Config:
    """Simple configuration loader for the knowledge management system."""
    
    def __init__(self, config_path="config/default.json"):
        """Load configuration from JSON file."""
        config_file = Path(config_path)
        with open(config_file, 'r') as f:
            self._config = json.load(f)
    
    def __getattr__(self, name):
        """Access config values as attributes."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"Config has no attribute '{name}'")
