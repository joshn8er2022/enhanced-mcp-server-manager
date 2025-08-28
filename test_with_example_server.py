#!/usr/bin/env python3
"""
Test the MCPServerManager with the example MCP server.
"""

import asyncio
import logging
import os
from mcp import StdioServerParameters
from mcp_server_manager import MCPServerManager


async def test_with_example_server():
    """Test the manager with our example MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Get the path to the example server
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "example_mcp_server.py")
    
    # Create server parameters
    server_params = [
        StdioServerParameters(
            command="python",
            args=[server_path]
        )
    ]
    
    # Create manager
    manager = MCPServerManager(server_params)
    
    try:
        logger.info("Testing with example MCP server...")
        
        async with manager.managed_connection():
            logger.info(f"Connected to {len(manager)} server(s)")
            
            # List all tools
            tools = await manager.tools()
            logger.info(f"Found {len(tools)} tools:")
            
            for tool in tools:
                print(f"  - {tool['name']}: {tool['doc']}")
                if tool.get('schema'):
                    print(f"    Schema: {tool['schema']}")
                print()
            
            # Test individual tools
            if tools:
                # Test echo tool
                echo_tool = await manager.get_tool_by_name("echo")
                if echo_tool:
                    logger.info("Testing echo tool...")
                    try:
                        result = await manager.execute_tool("echo", text="Hello, MCP!")
                        logger.info(f"Echo result: {result}")
                    except Exception as e:
                        logger.error(f"Echo tool failed: {e}")
                
                # Test add_numbers tool
                add_tool = await manager.get_tool_by_name("add_numbers")
                if add_tool:
                    logger.info("Testing add_numbers tool...")
                    try:
                        result = await manager.execute_tool("add_numbers", a=5, b=3)
                        logger.info(f"Add result: {result}")
                    except Exception as e:
                        logger.error(f"Add tool failed: {e}")
                
                # Test get_info tool
                info_tool = await manager.get_tool_by_name("get_info")
                if info_tool:
                    logger.info("Testing get_info tool...")
                    try:
                        result = await manager.execute_tool("get_info")
                        logger.info(f"Info result: {result}")
                    except Exception as e:
                        logger.error(f"Info tool failed: {e}")
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    print("Testing MCP Server Manager with example server...")
    asyncio.run(test_with_example_server())