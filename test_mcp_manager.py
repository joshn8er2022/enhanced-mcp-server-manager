#!/usr/bin/env python3
"""
Test script for the MCPServerManager.

This script demonstrates how to use the enhanced MCP Server Manager
with proper error handling and resource management.
"""

import asyncio
import logging
from mcp import StdioServerParameters
from mcp_server_manager import MCPServerManager


async def test_mcp_manager():
    """Test the MCP Server Manager with mock servers."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Example server parameters (these would need to point to actual MCP servers)
    server_params = [
        StdioServerParameters(
            command="python",
            args=["-c", "print('Mock MCP Server 1')"]  # Mock server for testing
        ),
        StdioServerParameters(
            command="python", 
            args=["-c", "print('Mock MCP Server 2')"]  # Mock server for testing
        )
    ]
    
    # Create manager
    manager = MCPServerManager(server_params)
    
    try:
        # Test manual connection
        logger.info("Testing manual connection...")
        await manager.connect_all()
        logger.info(f"Connected to {len(manager)} servers")
        
        # Test tool listing
        tools = await manager.tools()
        logger.info(f"Found {len(tools)} tools")
        
        # Clean up
        await manager.disconnect_all()
        logger.info("Manual connection test completed")
        
        # Test context manager
        logger.info("Testing context manager...")
        async with manager.managed_connection():
            logger.info(f"Context manager connected to {len(manager)} servers")
            tools = await manager.tools()
            logger.info(f"Found {len(tools)} tools via context manager")
        
        logger.info("Context manager test completed")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


async def test_with_real_servers():
    """
    Example of how to use with real MCP servers.
    
    Replace the paths below with actual MCP server implementations.
    """
    # Example with hypothetical real servers
    server_params = [
        StdioServerParameters(
            command="python",
            args=["/path/to/filesystem_mcp_server.py"]
        ),
        StdioServerParameters(
            command="python",
            args=["/path/to/web_search_mcp_server.py"]
        )
    ]
    
    manager = MCPServerManager(server_params)
    
    async with manager.managed_connection():
        # Get all tools
        tools = await manager.tools()
        
        print(f"Available tools from {len(manager)} servers:")
        for tool in tools:
            print(f"  Server {tool['server_index']}: {tool['name']}")
            print(f"    Description: {tool['doc']}")
            print()
        
        # Example: Execute a specific tool
        if tools:
            tool_name = tools[0]['name']
            try:
                # result = await manager.execute_tool(tool_name, **arguments)
                print(f"Would execute tool: {tool_name}")
            except Exception as e:
                print(f"Error executing {tool_name}: {e}")


if __name__ == "__main__":
    print("Running MCP Server Manager tests...")
    
    # Run the basic test
    asyncio.run(test_mcp_manager())
    
    print("\nFor real server testing, uncomment and modify test_with_real_servers()")
    # asyncio.run(test_with_real_servers())