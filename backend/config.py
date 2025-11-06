"""
Configuration loader for config.properties file.
Falls back to environment variables if config file not found.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager that loads from config.properties file."""
    
    def __init__(self):
        self.config_dict = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config.properties file."""
        # Get project root (parent of backend directory)
        project_root = Path(__file__).parent.parent
        config_file = project_root / "config.properties"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config_dict[key] = value
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key."""
        # First check config file
        value = self.config_dict.get(key)
        if value:
            return value
        
        # Fall back to environment variable
        value = os.environ.get(key)
        if value:
            return value
        
        # Return default if not found
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

