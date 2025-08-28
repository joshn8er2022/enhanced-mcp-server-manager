#!/usr/bin/env python3
"""
MCP Server Configuration Loader

This module provides utilities to load and manage MCP server configurations
from JSON files and create MCPServerManager instances with predefined setups.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from mcp import StdioServerParameters
from mcp_server_manager import MCPServerManager


class MCPConfigLoader:
    """Load and manage MCP server configurations from JSON files."""
    
    def __init__(self, config_path: str = "mcp_servers_config.json"):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get_all_servers(self) -> List[Dict[str, Any]]:
        """Get all available server configurations."""
        return self.config.get("mcp_servers", [])
    
    def get_server_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific server configuration by name."""
        for server in self.get_all_servers():
            if server["name"] == name:
                return server
        return None
    
    def get_servers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all servers in a specific category."""
        return [
            server for server in self.get_all_servers()
            if server.get("category") == category
        ]
    
    def get_categories(self) -> Dict[str, Any]:
        """Get all available categories."""
        return self.config.get("categories", {})
    
    def get_usage_examples(self) -> Dict[str, Any]:
        """Get predefined usage examples."""
        return self.config.get("usage_examples", {})
    
    def get_installation_commands(self) -> Dict[str, List[str]]:
        """Get installation commands for different server types."""
        return self.config.get("installation_commands", {})
    
    def create_server_params(self, server_names: List[str]) -> List[StdioServerParameters]:
        """
        Create StdioServerParameters for specified servers.
        
        Args:
            server_names: List of server names to create parameters for
            
        Returns:
            List of StdioServerParameters
            
        Raises:
            ValueError: If a server name is not found
        """
        params_list = []
        
        for name in server_names:
            server_config = self.get_server_by_name(name)
            if not server_config:
                raise ValueError(f"Server '{name}' not found in configuration")
            
            params = StdioServerParameters(
                command=server_config["command"],
                args=server_config["args"]
            )
            params_list.append(params)
            
        return params_list
    
    def create_manager_from_example(self, example_name: str) -> MCPServerManager:
        """
        Create an MCPServerManager from a predefined usage example.
        
        Args:
            example_name: Name of the usage example
            
        Returns:
            Configured MCPServerManager instance
            
        Raises:
            ValueError: If example name is not found
        """
        examples = self.get_usage_examples()
        if example_name not in examples:
            available = ", ".join(examples.keys())
            raise ValueError(f"Example '{example_name}' not found. Available: {available}")
        
        server_names = examples[example_name]["servers"]
        params_list = self.create_server_params(server_names)
        
        return MCPServerManager(params_list)
    
    def create_manager_from_category(self, category: str) -> MCPServerManager:
        """
        Create an MCPServerManager with all servers from a category.
        
        Args:
            category: Category name
            
        Returns:
            Configured MCPServerManager instance
        """
        servers = self.get_servers_by_category(category)
        if not servers:
            available = ", ".join(self.get_categories().keys())
            raise ValueError(f"Category '{category}' not found or empty. Available: {available}")
        
        server_names = [server["name"] for server in servers]
        params_list = self.create_server_params(server_names)
        
        return MCPServerManager(params_list)
    
    def create_custom_manager(self, server_names: List[str]) -> MCPServerManager:
        """
        Create an MCPServerManager with custom server selection.
        
        Args:
            server_names: List of server names to include
            
        Returns:
            Configured MCPServerManager instance
        """
        params_list = self.create_server_params(server_names)
        return MCPServerManager(params_list)
    
    def print_available_servers(self):
        """Print all available servers organized by category."""
        categories = self.get_categories()
        
        print("Available MCP Servers by Category:")
        print("=" * 50)
        
        for category_name, category_info in categories.items():
            print(f"\n{category_name.upper()}: {category_info['description']}")
            print("-" * 30)
            
            servers = self.get_servers_by_category(category_name)
            for server in servers:
                print(f"  • {server['name']}: {server['description']}")
                if server.get('requirements'):
                    print(f"    Requirements: {', '.join(server['requirements'])}")
                if server.get('security_note'):
                    print(f"    ⚠️  {server['security_note']}")
    
    def print_usage_examples(self):
        """Print all available usage examples."""
        examples = self.get_usage_examples()
        
        print("Predefined Usage Examples:")
        print("=" * 30)
        
        for example_name, example_info in examples.items():
            print(f"\n{example_name}: {example_info['description']}")
            print(f"  Servers: {', '.join(example_info['servers'])}")
    
    def print_installation_commands(self):
        """Print installation commands for all server types."""
        commands = self.get_installation_commands()
        
        print("Installation Commands:")
        print("=" * 25)
        
        for server_type, cmd_list in commands.items():
            print(f"\n{server_type.upper()} Servers:")
            for cmd in cmd_list:
                print(f"  {cmd}")


async def demo_config_loader():
    """Demonstrate the configuration loader functionality."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create config loader
    loader = MCPConfigLoader()
    
    # Print available servers
    loader.print_available_servers()
    print("\n" + "="*60 + "\n")
    
    # Print usage examples
    loader.print_usage_examples()
    print("\n" + "="*60 + "\n")
    
    # Create a manager from an example
    try:
        print("Creating manager from 'basic_setup' example...")
        manager = loader.create_manager_from_example("basic_setup")
        print(f"Created manager with {len(manager.server_params_list)} servers")
        
        # You could test the manager here if the servers are installed
        # async with manager.managed_connection():
        #     tools = await manager.tools()
        #     print(f"Found {len(tools)} tools")
        
    except Exception as e:
        print(f"Note: Could not test manager (servers may not be installed): {e}")
    
    # Show installation commands
    print("\n" + "="*60 + "\n")
    loader.print_installation_commands()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_config_loader())