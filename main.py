"""
Main application for the Enhanced MCP Server Manager.

This module implements the main loop with try/except/finally structure
where the MCP Manager agent is passed between blocks for proper error
handling and resource management.
"""

import asyncio
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime

import dspy

from models import BaseRequest, ReportOutput, ErrorReport, ReportType
from config import config_manager
from mcpman import MCPManager
from sig import MCPManagerSignature


class MCPManagerAgent(dspy.Module):
    """
    DSPy Module for MCP Manager operations.
    
    This agent uses the MCPManagerSignature to process requests and generate
    appropriate reports based on the operation type.
    """
    
    def __init__(self, mcp_manager: MCPManager):
        """
        Initialize the agent with an MCP Manager instance.
        
        Args:
            mcp_manager: The MCP Manager instance to use for operations
        """
        super().__init__()
        self.mcp_manager = mcp_manager
        self.signature = MCPManagerSignature
        self.logger = logging.getLogger(__name__)
    
    def forward(self, request: BaseRequest) -> ReportOutput:
        """
        Process a request and generate the appropriate report.
        
        Args:
            request: The request to process
            
        Returns:
            Appropriate report based on the operation
        """
        operation = getattr(request, 'operation', 'unknown')
        
        try:
            if operation == 'connect':
                # Handle server connection
                server_names = getattr(request, 'server_names', None)
                report = asyncio.run(self.mcp_manager.connect_servers(server_names))
                
            elif operation == 'discover':
                # Handle tool discovery
                report = asyncio.run(self.mcp_manager.discover_tools())
                
            elif operation == 'execute':
                # Handle tool execution
                tool_name = getattr(request, 'tool_name', '')
                tool_args = getattr(request, 'tool_args', {})
                report = asyncio.run(self.mcp_manager.execute_tool(tool_name, **tool_args))
                
            elif operation == 'performance':
                # Handle performance report
                report = self.mcp_manager.get_performance_report()
                
            elif operation == 'summary':
                # Handle summary report
                report = self.mcp_manager.get_summary_report()
                
            else:
                # Unknown operation
                raise ValueError(f"Unknown operation: {operation}")
            
            return report
            
        except Exception as e:
            # Return error report for any failures
            return ErrorReport(
                request_id=request.request_id,
                error_type=type(e).__name__,
                error_details=str(e),
                success=False,
                error_message=str(e)
            )


async def main_loop():
    """
    Main application loop with try/except/finally structure.
    
    The MCP Manager agent is passed between try, except, and finally blocks
    to ensure proper resource management and error handling.
    """
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config_manager.env_config.log_level),
        format=config_manager.env_config.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config_manager.env_config.log_file) 
            if config_manager.env_config.log_file else logging.NullHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Enhanced MCP Server Manager")
    
    # Initialize MCP Manager
    mcp_manager = MCPManager(config_manager)
    agent = None
    
    try:
        # Initialize the agent with proper tools
        logger.info("Initializing MCP Manager Agent")
        agent = MCPManagerAgent(mcp_manager)
        
        # Connect to servers
        logger.info("Connecting to MCP servers")
        connect_request = BaseRequest(
            operation="connect",
            server_names=None  # Connect to all enabled servers
        )
        
        connection_report = agent.forward(connect_request)
        logger.info(f"Connection result: {connection_report.success}")
        
        if not connection_report.success:
            logger.error(f"Failed to connect to servers: {connection_report.error_message}")
            return
        
        # Discover tools
        logger.info("Discovering available tools")
        discovery_request = BaseRequest(operation="discover")
        discovery_report = agent.forward(discovery_request)
        
        if discovery_report.success:
            logger.info(f"Discovered {len(discovery_report.discovered_tools)} tools")
            
            # Print discovered tools
            print("\n=== Discovered Tools ===")
            for tool in discovery_report.discovered_tools:
                print(f"  • {tool.name} ({tool.server_name}): {tool.description}")
        else:
            logger.error(f"Tool discovery failed: {discovery_report.error_message}")
        
        # Example tool execution (if tools are available)
        if discovery_report.success and discovery_report.discovered_tools:
            first_tool = discovery_report.discovered_tools[0]
            logger.info(f"Executing example tool: {first_tool.name}")
            
            execution_request = BaseRequest(
                operation="execute",
                tool_name=first_tool.name,
                tool_args={}  # Empty args for demo
            )
            
            execution_report = agent.forward(execution_request)
            
            if execution_report.success:
                logger.info(f"Tool execution successful: {execution_report.result}")
            else:
                logger.warning(f"Tool execution failed: {execution_report.error_message}")
        
        # Generate performance report
        logger.info("Generating performance report")
        perf_request = BaseRequest(operation="performance")
        perf_report = agent.forward(perf_request)
        
        print(f"\n=== Performance Report ===")
        print(f"Connected servers: {perf_report.resource_usage.get('connected_servers', 0)}")
        print(f"Discovered tools: {perf_report.resource_usage.get('discovered_tools', 0)}")
        print(f"Total operations: {perf_report.resource_usage.get('total_operations', 0)}")
        print(f"Error rate: {perf_report.error_rate:.2%}")
        
        # Generate summary report
        logger.info("Generating summary report")
        summary_request = BaseRequest(operation="summary")
        summary_report = agent.forward(summary_request)
        
        print(f"\n=== Summary Report ===")
        print(f"Operations: {summary_report.operation_summary}")
        print(f"Recommendations: {summary_report.recommendations}")
        
        logger.info("Main loop completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully")
        
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        
        # Generate error report using the agent if available
        if agent:
            error_request = BaseRequest(
                operation="error",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            error_report = ErrorReport(
                request_id=error_request.request_id,
                error_type=type(e).__name__,
                error_details=str(e),
                stack_trace=str(e),
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Generated error report: {error_report.dict()}")
    
    finally:
        # Cleanup resources - agent is passed to finally block
        logger.info("Cleaning up resources")
        
        if agent and agent.mcp_manager:
            try:
                # Disconnect all servers
                await agent.mcp_manager.disconnect_all()
                logger.info("Successfully disconnected from all servers")
                
                # Generate final summary
                final_summary = agent.mcp_manager.get_summary_report()
                logger.info(f"Final summary: {final_summary.operation_summary}")
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        logger.info("Enhanced MCP Server Manager shutdown complete")


async def interactive_mode():
    """
    Interactive mode for testing different operations.
    """
    print("=== Enhanced MCP Server Manager - Interactive Mode ===")
    
    mcp_manager = MCPManager(config_manager)
    agent = MCPManagerAgent(mcp_manager)
    
    try:
        # Connect to servers
        print("\n1. Connecting to servers...")
        connect_request = BaseRequest(operation="connect")
        connection_report = agent.forward(connect_request)
        
        if connection_report.success:
            print(f"✓ Connected to {len(connection_report.servers_connected)} servers")
        else:
            print(f"✗ Connection failed: {connection_report.error_message}")
            return
        
        # Discover tools
        print("\n2. Discovering tools...")
        discovery_request = BaseRequest(operation="discover")
        discovery_report = agent.forward(discovery_request)
        
        if discovery_report.success:
            print(f"✓ Discovered {len(discovery_report.discovered_tools)} tools")
            
            # Show available tools
            print("\nAvailable tools:")
            for i, tool in enumerate(discovery_report.discovered_tools[:10]):  # Show first 10
                print(f"  {i+1}. {tool.name} ({tool.server_name})")
        else:
            print(f"✗ Discovery failed: {discovery_report.error_message}")
            return
        
        # Interactive tool execution
        while True:
            print("\n3. Tool Operations:")
            print("  a) Execute a tool")
            print("  b) Performance report")
            print("  c) Summary report")
            print("  q) Quit")
            
            choice = input("\nEnter your choice: ").lower().strip()
            
            if choice == 'q':
                break
            elif choice == 'a':
                if discovery_report.discovered_tools:
                    tool_name = input("Enter tool name: ").strip()
                    execution_request = BaseRequest(
                        operation="execute",
                        tool_name=tool_name,
                        tool_args={}
                    )
                    execution_report = agent.forward(execution_request)
                    
                    if execution_report.success:
                        print(f"✓ Tool executed successfully")
                        print(f"Result: {execution_report.result}")
                    else:
                        print(f"✗ Execution failed: {execution_report.error_message}")
                else:
                    print("No tools available")
            
            elif choice == 'b':
                perf_request = BaseRequest(operation="performance")
                perf_report = agent.forward(perf_request)
                print(f"\nPerformance Report:")
                print(f"  Error rate: {perf_report.error_rate:.2%}")
                print(f"  Resource usage: {perf_report.resource_usage}")
            
            elif choice == 'c':
                summary_request = BaseRequest(operation="summary")
                summary_report = agent.forward(summary_request)
                print(f"\nSummary Report:")
                print(f"  Operations: {summary_report.operation_summary}")
                print(f"  Performance: {summary_report.performance_summary}")
    
    finally:
        await agent.mcp_manager.disconnect_all()
        print("\nDisconnected from all servers")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced MCP Server Manager")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Update config path if provided
    if args.config:
        global config_manager
        from config import ConfigManager
        config_manager = ConfigManager(args.config)
    
    # Run appropriate mode
    if args.interactive:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main_loop())


if __name__ == "__main__":
    main()