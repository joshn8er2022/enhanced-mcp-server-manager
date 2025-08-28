"""
Configuration management for MCP Server Manager using Pydantic.

This module handles loading and validation of configuration from various sources
including environment variables, JSON files, and runtime parameters.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from models import ServerConfig, MCPManagerConfig


class EnvironmentConfig(BaseSettings):
    """Environment-based configuration using Pydantic Settings."""
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Server Configuration
    default_timeout: int = Field(default=30, env="DEFAULT_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    connection_pool_size: int = Field(default=10, env="CONNECTION_POOL_SIZE")
    
    # Tool Execution
    tool_timeout: int = Field(default=60, env="TOOL_TIMEOUT")
    max_concurrent_tools: int = Field(default=5, env="MAX_CONCURRENT_TOOLS")
    
    # Security
    allowed_commands: str = Field(
        default="filesystem,git,sqlite,time,memory,fetch",
        env="ALLOWED_COMMANDS"
    )
    restricted_paths: str = Field(
        default="/etc,/root,/sys,/proc",
        env="RESTRICTED_PATHS"
    )
    enable_shell_commands: bool = Field(default=False, env="ENABLE_SHELL_COMMANDS")
    
    # Performance
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    
    # Development
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8080, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("allowed_commands")
    def parse_allowed_commands(cls, v):
        """Parse comma-separated allowed commands."""
        return [cmd.strip() for cmd in v.split(",") if cmd.strip()]
    
    @validator("restricted_paths")
    def parse_restricted_paths(cls, v):
        """Parse comma-separated restricted paths."""
        return [path.strip() for path in v.split(",") if path.strip()]


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to JSON configuration file
            env_file: Path to environment file
        """
        self.config_path = Path(config_path or "mcp_servers_config.json")
        self.env_file = env_file
        self._env_config = None
        self._server_configs = None
        self._manager_config = None
    
    @property
    def env_config(self) -> EnvironmentConfig:
        """Get environment configuration."""
        if self._env_config is None:
            if self.env_file:
                self._env_config = EnvironmentConfig(_env_file=self.env_file)
            else:
                self._env_config = EnvironmentConfig()
        return self._env_config
    
    def load_server_configs(self) -> List[ServerConfig]:
        """Load server configurations from JSON file."""
        if self._server_configs is None:
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                servers_data = data.get("mcp_servers", [])
                self._server_configs = [
                    ServerConfig(**server_data) for server_data in servers_data
                ]
                
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in configuration file: {e}")
            except Exception as e:
                raise ValueError(f"Error loading server configurations: {e}")
        
        return self._server_configs
    
    def get_manager_config(self) -> MCPManagerConfig:
        """Get complete manager configuration."""
        if self._manager_config is None:
            env_config = self.env_config
            server_configs = self.load_server_configs()
            
            # Create security settings from environment
            security_settings = {
                "allowed_commands": env_config.allowed_commands,
                "restricted_paths": env_config.restricted_paths,
                "enable_shell_commands": env_config.enable_shell_commands
            }
            
            # Create performance settings from environment
            performance_settings = {
                "cache_enabled": env_config.cache_enabled,
                "cache_ttl": env_config.cache_ttl,
                "batch_size": env_config.batch_size,
                "enable_metrics": env_config.enable_metrics,
                "metrics_port": env_config.metrics_port
            }
            
            self._manager_config = MCPManagerConfig(
                servers=server_configs,
                default_timeout=env_config.default_timeout,
                max_retries=env_config.max_retries,
                connection_pool_size=env_config.connection_pool_size,
                tool_timeout=env_config.tool_timeout,
                max_concurrent_tools=env_config.max_concurrent_tools,
                cache_enabled=env_config.cache_enabled,
                cache_ttl=env_config.cache_ttl,
                debug_mode=env_config.debug_mode,
                log_level=env_config.log_level,
                security_settings=security_settings,
                performance_settings=performance_settings
            )
        
        return self._manager_config
    
    def get_servers_by_category(self, category: str) -> List[ServerConfig]:
        """Get servers filtered by category."""
        servers = self.load_server_configs()
        return [server for server in servers if server.category == category]
    
    def get_server_by_name(self, name: str) -> Optional[ServerConfig]:
        """Get a specific server configuration by name."""
        servers = self.load_server_configs()
        for server in servers:
            if server.name == name:
                return server
        return None
    
    def get_enabled_servers(self) -> List[ServerConfig]:
        """Get only enabled server configurations."""
        servers = self.load_server_configs()
        return [server for server in servers if server.enabled]
    
    def validate_security_settings(self, server_name: str, command: str) -> bool:
        """Validate if a command is allowed for security."""
        env_config = self.env_config
        
        # Check if command is in allowed list
        if command not in env_config.allowed_commands:
            return False
        
        # Check for shell commands if disabled
        if not env_config.enable_shell_commands and command == "shell":
            return False
        
        return True
    
    def is_path_restricted(self, path: str) -> bool:
        """Check if a path is in the restricted list."""
        env_config = self.env_config
        path = os.path.abspath(path)
        
        for restricted_path in env_config.restricted_paths:
            if path.startswith(restricted_path):
                return True
        
        return False
    
    def get_usage_examples(self) -> Dict[str, Any]:
        """Get predefined usage examples from configuration."""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return data.get("usage_examples", {})
        except Exception:
            return {}
    
    def get_categories(self) -> Dict[str, Any]:
        """Get available categories from configuration."""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return data.get("categories", {})
        except Exception:
            return {}
    
    def get_installation_commands(self) -> Dict[str, List[str]]:
        """Get installation commands from configuration."""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            return data.get("installation_commands", {})
        except Exception:
            return {}
    
    def reload_config(self):
        """Reload all configurations from files."""
        self._env_config = None
        self._server_configs = None
        self._manager_config = None


# Global configuration instance
config_manager = ConfigManager()