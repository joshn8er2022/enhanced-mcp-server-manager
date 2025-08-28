from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import dspy
import asyncio
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

class MCPServerManager:
    """
    Enhanced MCP Server Manager for handling multiple MCP servers and their tools.
    
    This class manages connections to multiple MCP servers, provides unified tool access,
    and handles proper resource cleanup.
    """
    
    def __init__(self, server_params_list: List[StdioServerParameters]):
        """
        Initialize the MCP Server Manager.
        
        Args:
            server_params_list: List of StdioServerParameters for each MCP server
        """
        self.server_params_list = server_params_list
        self.sessions = []
        self.clients = []
        self.logger = logging.getLogger(__name__)
        
    async def connect_all(self):
        """Connect to all MCP servers and initialize sessions."""
        self.sessions = []
        self.clients = []
        
        for i, params in enumerate(self.server_params_list):
            try:
                # Create stdio client
                client = stdio_client(params)
                read, write = await client.__aenter__()
                self.clients.append(client)
                
                # Create and initialize session
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()
                
                self.sessions.append(session)
                self.logger.info(f"Successfully connected to MCP server {i+1}")
                
            except Exception as e:
                self.logger.error(f"Failed to connect to MCP server {i+1}: {e}")
                # Continue with other servers even if one fails
                continue
    
    async def disconnect_all(self):
        """Properly disconnect from all MCP servers and clean up resources."""
        for session in self.sessions:
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error disconnecting session: {e}")
        
        for client in self.clients:
            try:
                await client.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error disconnecting client: {e}")
        
        self.sessions = []
        self.clients = []
    
    async def tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools from all connected MCP servers.
        
        Returns:
            List of dictionaries containing tool information with keys:
            - name: Tool name
            - doc: Tool documentation
            - server_index: Index of the server providing this tool
            - dspy_tool: The DSPy tool object
        """
        all_tools = []
        
        for server_index, session in enumerate(self.sessions):
            try:
                tools_response = await session.list_tools()
                
                for tool in tools_response.tools:
                    try:
                        dspy_tool = dspy.Tool.from_mcp_tool(session, tool)
                        doc = getattr(dspy_tool.func, "__doc__", "") or tool.description or ""
                        
                        tool_info = {
                            "name": dspy_tool.name,
                            "doc": doc,
                            "server_index": server_index,
                            "dspy_tool": dspy_tool,
                            "schema": tool.inputSchema if hasattr(tool, 'inputSchema') else None
                        }
                        all_tools.append(tool_info)
                        
                    except Exception as e:
                        self.logger.error(f"Error creating DSPy tool for {tool.name}: {e}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Error listing tools from server {server_index}: {e}")
                continue
        
        return all_tools
    
    async def get_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool information dictionary or None if not found
        """
        tools = await self.tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        return None
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool is not found
        """
        tool_info = await self.get_tool_by_name(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        dspy_tool = tool_info["dspy_tool"]
        return await dspy_tool.func(**kwargs)
    
    @asynccontextmanager
    async def managed_connection(self):
        """
        Context manager for automatic connection and cleanup.
        
        Usage:
            async with manager.managed_connection():
                tools = await manager.tools()
                # Use tools...
        """
        try:
            await self.connect_all()
            yield self
        finally:
            await self.disconnect_all()
    
    def __len__(self) -> int:
        """Return the number of connected sessions."""
        return len(self.sessions)
    
    def is_connected(self) -> bool:
        """Check if any servers are connected."""
        return len(self.sessions) > 0


async def main():
    """Example usage of the MCPServerManager."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example server parameters (replace with actual server paths)
    server_params1 = StdioServerParameters(
        command="python", 
        args=["/path/to/mcp_server1.py"]
    )
    server_params2 = StdioServerParameters(
        command="python", 
        args=["/path/to/mcp_server2.py"]
    )
    
    # Create manager
    manager = MCPServerManager([server_params1, server_params2])
    
    # Use context manager for automatic cleanup
    async with manager.managed_connection():
        print(f"Connected to {len(manager)} MCP servers")
        
        # Get all available tools
        tools = await manager.tools()
        print(f"Found {len(tools)} tools:")
        
        for tool in tools:
            print(f"  - {tool['name']}: {tool['doc'][:100]}...")
        
        # Example: Execute a specific tool (if it exists)
        if tools:
            first_tool = tools[0]
            print(f"\nTrying to execute tool: {first_tool['name']}")
            try:
                # result = await manager.execute_tool(first_tool['name'], **some_args)
                # print(f"Result: {result}")
                pass
            except Exception as e:
                print(f"Error executing tool: {e}")


if __name__ == "__main__":
    asyncio.run(main())