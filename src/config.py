import json
from pathlib import Path


class Config:
    """Simple configuration loader for the knowledge management system."""
    
    def __init__(self, config_path=None):
        """Load configuration from JSON file."""
        if config_path is None:
            raise ValueError("Config path cannot be None. Use config_loader.find_config_file() to discover config.")
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_file}: {e}")
        
        # Validate required keys
        required_keys = ['knowledge_base_root', 'chroma_db_path', 'chunk_size', 'chunk_overlap']
        missing_keys = [key for key in required_keys if key not in self._config]
        if missing_keys:
            raise ValueError(f"Missing required config keys: {missing_keys}")
    
    def __getattr__(self, name):
        """Access config values as attributes."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"Config has no attribute '{name}'")
