"""
MCP Manager - Core agent for managing MCP servers and tool execution.

This module contains the main MCPManager class that handles server connections,
tool discovery, execution, and report generation with proper error handling.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import dspy

from models import (
    BaseRequest, ReportOutput, ToolInfo, ServerInfo, ServerStatus,
    ToolExecutionStatus, ConnectionReport, ToolDiscoveryReport,
    ToolExecutionReport, ErrorReport, PerformanceReport, SummaryReport
)
from config import ConfigManager, config_manager


class MCPManager:
    """
    Core MCP Manager agent for handling server connections and tool operations.
    
    This class manages the lifecycle of MCP server connections, provides tool
    discovery and execution capabilities, and generates comprehensive reports
    for all operations.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the MCP Manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or config_manager
        self.logger = logging.getLogger(__name__)
        
        # Connection management
        self.sessions: List[ClientSession] = []
        self.clients: List[Any] = []
        self.server_info: List[ServerInfo] = []
        
        # Tool management
        self.discovered_tools: List[ToolInfo] = []
        self.tool_cache: Dict[str, Any] = {}
        
        # Performance tracking
        self.operation_metrics: Dict[str, float] = {}
        self.error_count: int = 0
        self.success_count: int = 0
        
        # Load configuration
        self.manager_config = self.config_manager.get_manager_config()
    
    async def connect_servers(self, server_names: Optional[List[str]] = None) -> ConnectionReport:
        """
        Connect to specified MCP servers.
        
        Args:
            server_names: List of server names to connect to. If None, connects to all enabled servers.
            
        Returns:
            ConnectionReport with connection results
        """
        start_time = time.time()
        request_id = f"connect_{datetime.now().timestamp()}"
        
        try:
            # Get server configurations
            if server_names:
                servers_to_connect = [
                    self.config_manager.get_server_by_name(name)
                    for name in server_names
                    if self.config_manager.get_server_by_name(name)
                ]
            else:
                servers_to_connect = self.config_manager.get_enabled_servers()
            
            servers_connected = []
            servers_failed = []
            
            # Clear existing connections
            await self.disconnect_all()
            
            # Connect to each server
            for server_config in servers_to_connect:
                server_info = ServerInfo(
                    name=server_config.name,
                    command=server_config.command,
                    args=server_config.args,
                    status=ServerStatus.CONNECTING
                )
                
                try:
                    # Validate security settings
                    if not self.config_manager.validate_security_settings(
                        server_config.name, server_config.command
                    ):
                        raise ValueError(f"Security validation failed for {server_config.name}")
                    
                    # Create server parameters
                    params = StdioServerParameters(
                        command=server_config.command,
                        args=server_config.args
                    )
                    
                    # Create and connect client
                    client = stdio_client(params)
                    read, write = await asyncio.wait_for(
                        client.__aenter__(),
                        timeout=server_config.timeout
                    )
                    self.clients.append(client)
                    
                    # Create and initialize session
                    session = ClientSession(read, write)
                    await session.__aenter__()
                    await asyncio.wait_for(
                        session.initialize(),
                        timeout=server_config.timeout
                    )
                    
                    self.sessions.append(session)
                    
                    # Update server info
                    server_info.status = ServerStatus.CONNECTED
                    server_info.connection_time = datetime.now()
                    servers_connected.append(server_info)
                    
                    self.logger.info(f"Successfully connected to {server_config.name}")
                    
                except Exception as e:
                    server_info.status = ServerStatus.ERROR
                    server_info.last_error = str(e)
                    servers_failed.append(server_info)
                    
                    self.logger.error(f"Failed to connect to {server_config.name}: {e}")
                    self.error_count += 1
                
                self.server_info.append(server_info)
            
            # Calculate success rate
            total_servers = len(servers_to_connect)
            connected_count = len(servers_connected)
            success_rate = connected_count / total_servers if total_servers > 0 else 0.0
            
            execution_time = time.time() - start_time
            self.operation_metrics["last_connection_time"] = execution_time
            
            # Create connection report
            report = ConnectionReport(
                request_id=request_id,
                servers_connected=servers_connected,
                servers_failed=servers_failed,
                total_servers=total_servers,
                connection_success_rate=success_rate,
                execution_time=execution_time,
                success=connected_count > 0
            )
            
            if connected_count > 0:
                self.success_count += 1
            else:
                self.error_count += 1
                report.error_message = "No servers connected successfully"
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            return ConnectionReport(
                request_id=request_id,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def discover_tools(self) -> ToolDiscoveryReport:
        """
        Discover all available tools from connected servers.
        
        Returns:
            ToolDiscoveryReport with discovered tools
        """
        start_time = time.time()
        request_id = f"discover_{datetime.now().timestamp()}"
        
        try:
            discovered_tools = []
            tools_by_server = {}
            categories = set()
            
            for server_index, session in enumerate(self.sessions):
                server_info = self.server_info[server_index]
                server_tools = []
                
                try:
                    # List tools from server
                    tools_response = await asyncio.wait_for(
                        session.list_tools(),
                        timeout=self.manager_config.tool_timeout
                    )
                    
                    for tool in tools_response.tools:
                        try:
                            # Create DSPy tool
                            dspy_tool = dspy.Tool.from_mcp_tool(session, tool)
                            
                            # Create tool info
                            tool_info = ToolInfo(
                                name=dspy_tool.name,
                                description=getattr(dspy_tool.func, "__doc__", "") or tool.description or "",
                                server_index=server_index,
                                server_name=server_info.name,
                                input_schema=tool.inputSchema if hasattr(tool, 'inputSchema') else None,
                                capabilities=getattr(tool, 'capabilities', []),
                                status=ToolExecutionStatus.PENDING
                            )
                            
                            discovered_tools.append(tool_info)
                            server_tools.append(tool_info)
                            
                            # Add to categories
                            server_config = self.config_manager.get_server_by_name(server_info.name)
                            if server_config:
                                categories.add(server_config.category)
                            
                        except Exception as e:
                            self.logger.error(f"Error creating tool {tool.name}: {e}")
                            continue
                    
                    # Update server tool count
                    server_info.tool_count = len(server_tools)
                    tools_by_server[server_info.name] = server_tools
                    
                except Exception as e:
                    self.logger.error(f"Error listing tools from {server_info.name}: {e}")
                    tools_by_server[server_info.name] = []
                    continue
            
            # Cache discovered tools
            self.discovered_tools = discovered_tools
            
            execution_time = time.time() - start_time
            self.operation_metrics["last_discovery_time"] = execution_time
            
            # Create discovery report
            report = ToolDiscoveryReport(
                request_id=request_id,
                discovered_tools=discovered_tools,
                tools_by_server=tools_by_server,
                total_tools=len(discovered_tools),
                categories=list(categories),
                execution_time=execution_time,
                success=True
            )
            
            self.success_count += 1
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            return ToolDiscoveryReport(
                request_id=request_id,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolExecutionReport:
        """
        Execute a specific tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            ToolExecutionReport with execution results
        """
        start_time = time.time()
        request_id = f"execute_{tool_name}_{datetime.now().timestamp()}"
        
        try:
            # Find the tool
            tool_info = None
            dspy_tool = None
            
            for tool in self.discovered_tools:
                if tool.name == tool_name:
                    tool_info = tool
                    # Get the session for this tool
                    session = self.sessions[tool.server_index]
                    
                    # Recreate DSPy tool (since we don't store it)
                    tools_response = await session.list_tools()
                    for mcp_tool in tools_response.tools:
                        if mcp_tool.name == tool_name:
                            dspy_tool = dspy.Tool.from_mcp_tool(session, mcp_tool)
                            break
                    break
            
            if not tool_info or not dspy_tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Execute the tool
            result = await asyncio.wait_for(
                dspy_tool.func(**kwargs),
                timeout=self.manager_config.tool_timeout
            )
            
            execution_time = time.time() - start_time
            
            # Update tool info
            tool_info.execution_time = execution_time
            tool_info.status = ToolExecutionStatus.SUCCESS
            
            # Create execution report
            report = ToolExecutionReport(
                request_id=request_id,
                tool_name=tool_name,
                tool_args=kwargs,
                result=result,
                execution_status=ToolExecutionStatus.SUCCESS,
                server_name=tool_info.server_name,
                tools_used=[tool_info],
                execution_time=execution_time,
                success=True
            )
            
            self.success_count += 1
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            # Update tool info if found
            if tool_info:
                tool_info.execution_time = execution_time
                tool_info.status = ToolExecutionStatus.FAILED
                tool_info.error_message = str(e)
            
            return ToolExecutionReport(
                request_id=request_id,
                tool_name=tool_name,
                tool_args=kwargs,
                execution_status=ToolExecutionStatus.FAILED,
                server_name=tool_info.server_name if tool_info else "",
                tools_used=[tool_info] if tool_info else [],
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def disconnect_all(self):
        """Disconnect from all servers and clean up resources."""
        # Disconnect sessions
        for session in self.sessions:
            try:
                await session.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error disconnecting session: {e}")
        
        # Disconnect clients
        for client in self.clients:
            try:
                await client.__aexit__(None, None, None)
            except Exception as e:
                self.logger.error(f"Error disconnecting client: {e}")
        
        # Clear collections
        self.sessions.clear()
        self.clients.clear()
        self.server_info.clear()
        self.discovered_tools.clear()
    
    def get_performance_report(self) -> PerformanceReport:
        """Generate a performance report."""
        request_id = f"perf_{datetime.now().timestamp()}"
        
        total_operations = self.success_count + self.error_count
        error_rate = self.error_count / total_operations if total_operations > 0 else 0.0
        
        return PerformanceReport(
            request_id=request_id,
            avg_response_time=self.operation_metrics.get("avg_response_time", 0.0),
            max_response_time=self.operation_metrics.get("max_response_time", 0.0),
            min_response_time=self.operation_metrics.get("min_response_time", 0.0),
            throughput=total_operations,
            error_rate=error_rate,
            resource_usage={
                "connected_servers": len(self.sessions),
                "discovered_tools": len(self.discovered_tools),
                "total_operations": total_operations
            },
            success=True
        )
    
    def get_summary_report(self) -> SummaryReport:
        """Generate a summary report of all operations."""
        request_id = f"summary_{datetime.now().timestamp()}"
        
        return SummaryReport(
            request_id=request_id,
            operation_summary={
                "connections": len(self.server_info),
                "tools_discovered": len(self.discovered_tools),
                "successful_operations": self.success_count,
                "failed_operations": self.error_count
            },
            performance_summary=self.operation_metrics,
            error_summary={
                "total_errors": self.error_count,
                "error_rate": self.error_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0.0
            },
            recommendations=[
                "Monitor error rates and investigate failed connections",
                "Consider caching frequently used tools",
                "Review server timeout settings if connections are failing"
            ],
            success=True
        )
    
    @asynccontextmanager
    async def managed_session(self, server_names: Optional[List[str]] = None):
        """
        Context manager for automatic connection and cleanup.
        
        Args:
            server_names: List of server names to connect to
            
        Yields:
            MCPManager instance with active connections
        """
        try:
            await self.connect_servers(server_names)
            yield self
        finally:
            await self.disconnect_all()
    
    def is_connected(self) -> bool:
        """Check if any servers are connected."""
        return len(self.sessions) > 0
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names."""
        return [
            info.name for info in self.server_info
            if info.status == ServerStatus.CONNECTED
        ]
    
    def get_tool_by_name(self, tool_name: str) -> Optional[ToolInfo]:
        """Get tool information by name."""
        for tool in self.discovered_tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_tools_by_server(self, server_name: str) -> List[ToolInfo]:
        """Get all tools from a specific server."""
        return [
            tool for tool in self.discovered_tools
            if tool.server_name == server_name
        ]