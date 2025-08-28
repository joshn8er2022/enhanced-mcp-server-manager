#!/usr/bin/env python3
"""
MCP Server Installation Helper

This script helps install MCP servers based on the configuration file.
It provides options to install specific servers, categories, or usage examples.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse


class MCPServerInstaller:
    """Helper class to install MCP servers."""
    
    def __init__(self, config_path: str = "mcp_servers_config.json"):
        """Initialize the installer with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _run_command(self, command: str) -> bool:
        """Run a shell command and return success status."""
        try:
            print(f"Running: {command}")
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
            print(f"✓ Success: {command}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed: {command}")
            print(f"  Error: {e.stderr}")
            return False
    
    def install_node_servers(self, server_names: List[str] = None) -> bool:
        """Install Node.js-based MCP servers."""
        commands = self.config.get("installation_commands", {}).get("node_servers", [])
        
        if server_names:
            # Filter commands for specific servers
            filtered_commands = []
            for server_name in server_names:
                for cmd in commands:
                    if server_name in cmd:
                        filtered_commands.append(cmd)
            commands = filtered_commands
        
        print(f"Installing {len(commands)} Node.js-based MCP servers...")
        
        success_count = 0
        for cmd in commands:
            if self._run_command(cmd):
                success_count += 1
        
        print(f"Successfully installed {success_count}/{len(commands)} Node.js servers")
        return success_count == len(commands)
    
    def install_python_servers(self, server_names: List[str] = None) -> bool:
        """Install Python-based MCP servers."""
        commands = self.config.get("installation_commands", {}).get("python_servers", [])
        
        if server_names:
            # Filter commands for specific servers
            filtered_commands = []
            for server_name in server_names:
                for cmd in commands:
                    if server_name in cmd:
                        filtered_commands.append(cmd)
            commands = filtered_commands
        
        print(f"Installing {len(commands)} Python-based MCP servers...")
        
        success_count = 0
        for cmd in commands:
            if self._run_command(cmd):
                success_count += 1
        
        print(f"Successfully installed {success_count}/{len(commands)} Python servers")
        return success_count == len(commands)
    
    def install_by_example(self, example_name: str) -> bool:
        """Install servers for a specific usage example."""
        examples = self.config.get("usage_examples", {})
        if example_name not in examples:
            print(f"Example '{example_name}' not found")
            return False
        
        server_names = examples[example_name]["servers"]
        print(f"Installing servers for '{example_name}' example: {', '.join(server_names)}")
        
        return self.install_servers(server_names)
    
    def install_by_category(self, category: str) -> bool:
        """Install all servers in a specific category."""
        servers = [s for s in self.config.get("mcp_servers", []) 
                  if s.get("category") == category]
        
        if not servers:
            print(f"Category '{category}' not found or empty")
            return False
        
        server_names = [s["name"] for s in servers]
        print(f"Installing servers for '{category}' category: {', '.join(server_names)}")
        
        return self.install_servers(server_names)
    
    def install_servers(self, server_names: List[str]) -> bool:
        """Install specific servers by name."""
        # Separate servers by type
        node_servers = []
        python_servers = []
        
        for server_name in server_names:
            server_config = self._get_server_config(server_name)
            if not server_config:
                print(f"Server '{server_name}' not found in configuration")
                continue
            
            if server_config["command"] == "npx":
                node_servers.append(server_name)
            elif server_config["command"] == "python":
                python_servers.append(server_name)
        
        success = True
        
        if node_servers:
            success &= self.install_node_servers(node_servers)
        
        if python_servers:
            success &= self.install_python_servers(python_servers)
        
        return success
    
    def _get_server_config(self, server_name: str) -> Dict[str, Any]:
        """Get configuration for a specific server."""
        for server in self.config.get("mcp_servers", []):
            if server["name"] == server_name:
                return server
        return None
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed."""
        print("Checking prerequisites...")
        
        # Check Node.js
        node_ok = self._run_command("node --version")
        npm_ok = self._run_command("npm --version")
        
        # Check Python
        python_ok = self._run_command("python --version") or self._run_command("python3 --version")
        pip_ok = self._run_command("pip --version") or self._run_command("pip3 --version")
        
        all_ok = node_ok and npm_ok and python_ok and pip_ok
        
        if all_ok:
            print("✓ All prerequisites are available")
        else:
            print("✗ Some prerequisites are missing")
            if not (node_ok and npm_ok):
                print("  Install Node.js and npm")
            if not (python_ok and pip_ok):
                print("  Install Python and pip")
        
        return all_ok
    
    def list_available_options(self):
        """List all available installation options."""
        print("Available installation options:")
        print("\n1. Usage Examples:")
        examples = self.config.get("usage_examples", {})
        for name, info in examples.items():
            print(f"   {name}: {info['description']}")
        
        print("\n2. Categories:")
        categories = self.config.get("categories", {})
        for name, info in categories.items():
            print(f"   {name}: {info['description']}")
        
        print("\n3. Individual Servers:")
        servers = self.config.get("mcp_servers", [])
        for server in servers:
            print(f"   {server['name']}: {server['description']}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Install MCP servers")
    parser.add_argument("--check", action="store_true", 
                       help="Check prerequisites")
    parser.add_argument("--list", action="store_true",
                       help="List available installation options")
    parser.add_argument("--example", type=str,
                       help="Install servers for a usage example")
    parser.add_argument("--category", type=str,
                       help="Install servers for a category")
    parser.add_argument("--servers", nargs="+",
                       help="Install specific servers by name")
    parser.add_argument("--all-node", action="store_true",
                       help="Install all Node.js-based servers")
    parser.add_argument("--all-python", action="store_true",
                       help="Install all Python-based servers")
    
    args = parser.parse_args()
    
    installer = MCPServerInstaller()
    
    if args.check:
        installer.check_prerequisites()
        return
    
    if args.list:
        installer.list_available_options()
        return
    
    if not installer.check_prerequisites():
        print("Please install missing prerequisites first")
        return
    
    if args.example:
        installer.install_by_example(args.example)
    elif args.category:
        installer.install_by_category(args.category)
    elif args.servers:
        installer.install_servers(args.servers)
    elif args.all_node:
        installer.install_node_servers()
    elif args.all_python:
        installer.install_python_servers()
    else:
        print("No installation option specified. Use --help for options.")
        installer.list_available_options()


if __name__ == "__main__":
    main()