#!/usr/bin/env python3
"""
Example MCP Server for testing the MCPServerManager.

This is a simple MCP server that provides basic tools for demonstration purposes.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Create server instance
server = Server("example-mcp-server")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="echo",
            description="Echo back the input text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="add_numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="get_info",
            description="Get server information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "echo":
        text = arguments.get("text", "")
        return [TextContent(type="text", text=f"Echo: {text}")]
    
    elif name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return [TextContent(type="text", text=f"Result: {a} + {b} = {result}")]
    
    elif name == "get_info":
        info = {
            "server_name": "example-mcp-server",
            "version": "1.0.0",
            "tools_count": 3,
            "status": "running"
        }
        return [TextContent(type="text", text=json.dumps(info, indent=2))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())