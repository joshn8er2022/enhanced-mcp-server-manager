#!/usr/bin/env python3
"""
Example usage of the MCP Server Manager with configuration loader.

This script demonstrates various ways to use the enhanced MCP Server Manager
with predefined server configurations.
"""

import asyncio
import logging
from mcp_config_loader import MCPConfigLoader
from mcp_server_manager import MCPServerManager


async def example_basic_setup():
    """Example using the basic setup configuration."""
    print("=== Basic Setup Example ===")
    
    loader = MCPConfigLoader()
    
    try:
        # Create manager from predefined example
        manager = loader.create_manager_from_example("basic_setup")
        print(f"Created manager with {len(manager.server_params_list)} servers")
        
        # List the servers that would be used
        example_info = loader.get_usage_examples()["basic_setup"]
        print(f"Servers: {', '.join(example_info['servers'])}")
        
        # Note: Actual connection would require the servers to be installed
        print("Note: To actually connect, install the required servers first")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_custom_selection():
    """Example using custom server selection."""
    print("\n=== Custom Selection Example ===")
    
    loader = MCPConfigLoader()
    
    try:
        # Create manager with custom server selection
        custom_servers = ["filesystem", "time", "memory"]
        manager = loader.create_custom_manager(custom_servers)
        print(f"Created custom manager with servers: {', '.join(custom_servers)}")
        
        # Show server details
        for server_name in custom_servers:
            server_info = loader.get_server_by_name(server_name)
            if server_info:
                print(f"  • {server_name}: {server_info['description']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_category_based():
    """Example using category-based server selection."""
    print("\n=== Category-Based Example ===")
    
    loader = MCPConfigLoader()
    
    try:
        # Create manager with all servers from a category
        category = "data_processing"
        manager = loader.create_manager_from_category(category)
        
        servers = loader.get_servers_by_category(category)
        server_names = [s["name"] for s in servers]
        print(f"Created manager with {category} servers: {', '.join(server_names)}")
        
        # Show capabilities
        for server in servers:
            capabilities = server.get("capabilities", [])
            print(f"  • {server['name']}: {', '.join(capabilities)}")
        
    except Exception as e:
        print(f"Error: {e}")


async def example_with_actual_servers():
    """
    Example that would work with actual installed servers.
    
    This demonstrates how to use the manager once servers are installed.
    """
    print("\n=== Actual Server Usage Example ===")
    print("(This would work if servers were installed)")
    
    loader = MCPConfigLoader()
    
    # Example code that would work with installed servers
    example_code = '''
    # Install servers first:
    # npm install -g @modelcontextprotocol/server-filesystem
    # npm install -g @modelcontextprotocol/server-time
    
    manager = loader.create_custom_manager(["filesystem", "time"])
    
    async with manager.managed_connection():
        print(f"Connected to {len(manager)} servers")
        
        # List all available tools
        tools = await manager.tools()
        print(f"Available tools: {len(tools)}")
        
        for tool in tools:
            print(f"  - {tool['name']}: {tool['doc']}")
        
        # Execute a tool (example)
        if tools:
            # result = await manager.execute_tool("list_directory", path="/workspace")
            # print(f"Directory listing: {result}")
            pass
    '''
    
    print(example_code)


def show_installation_guide():
    """Show installation guide for different server types."""
    print("\n=== Installation Guide ===")
    
    loader = MCPConfigLoader()
    
    print("To use these MCP servers, install them first:")
    print("\n1. Node.js-based servers (using npm):")
    node_commands = loader.get_installation_commands().get("node_servers", [])
    for cmd in node_commands[:5]:  # Show first 5
        print(f"   {cmd}")
    print("   ... (see mcp_servers_config.json for complete list)")
    
    print("\n2. Python-based servers (using pip):")
    python_commands = loader.get_installation_commands().get("python_servers", [])
    for cmd in python_commands[:5]:  # Show first 5
        print(f"   {cmd}")
    print("   ... (see mcp_servers_config.json for complete list)")
    
    print("\n3. System requirements:")
    print("   - Node.js 16+ for NPX-based servers")
    print("   - Python 3.8+ for Python-based servers")
    print("   - Docker for Docker server")
    print("   - kubectl configured for Kubernetes server")


def show_security_considerations():
    """Show security considerations for different servers."""
    print("\n=== Security Considerations ===")
    
    loader = MCPConfigLoader()
    security_info = loader.config.get("security_considerations", {})
    
    for server, warning in security_info.items():
        print(f"⚠️  {server}: {warning}")


async def main():
    """Main demonstration function."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("MCP Server Manager Configuration Examples")
    print("=" * 50)
    
    # Show available servers
    loader = MCPConfigLoader()
    loader.print_available_servers()
    
    # Run examples
    await example_basic_setup()
    await example_custom_selection()
    await example_category_based()
    await example_with_actual_servers()
    
    # Show guides
    show_installation_guide()
    show_security_considerations()
    
    print("\n" + "=" * 50)
    print("For more details, see:")
    print("- mcp_servers_config.json: Complete server configurations")
    print("- README.md: Usage documentation")
    print("- FIXES_AND_ENHANCEMENTS.md: Technical details")


if __name__ == "__main__":
    asyncio.run(main())