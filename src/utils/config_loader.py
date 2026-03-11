"""
Utility functions for configuration loading
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration settings"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._load_env_vars()
        self._create_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def _load_env_vars(self):
        """Load environment variables from .env file"""
        load_dotenv()
        
        # Replace placeholders in config with environment variables
        if 'api_keys' in self.config:
            for key, value in self.config['api_keys'].items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    self.config['api_keys'][key] = os.getenv(env_var, '')
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        if 'paths' in self.config:
            for path_name, path_value in self.config['paths'].items():
                Path(path_value).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., 'transcription.model')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self.config
    
    def get_video_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured video sources"""
        return self.config.get('video_sources', {})
    
    def get_api_key(self, provider: str) -> str:
        """
        Get API key for specified provider
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
        
        Returns:
            API key string
        """
        key_name = f"{provider}_api_key"
        return self.config.get('api_keys', {}).get(key_name, '')
