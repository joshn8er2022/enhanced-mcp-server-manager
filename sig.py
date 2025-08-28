"""
Signature definition for the MCP Manager agent.

This module defines the single signature that the MCP Manager uses for
processing requests and generating reports. The signature accepts any
input through a flexible base model and returns one of many possible
report types.
"""

import dspy
from typing import Union
from models import BaseRequest, ReportOutput


class MCPManagerSignature(dspy.Signature):
    """
    Single signature for MCP Manager operations.
    
    This signature defines the interface for the MCP Manager agent:
    - Input: BaseRequest that accepts any fields through **kwargs at runtime
    - Output: Union of all possible report types (20+ different report types)
    
    The agent processes the request and determines the appropriate report type
    based on the operation being performed.
    """
    
    # Input: Flexible base model that accepts any additional fields
    request: BaseRequest = dspy.InputField(
        desc="Request containing operation details and parameters. "
             "Accepts any additional fields through **kwargs at runtime."
    )
    
    # Output: Union of all possible report types
    report: ReportOutput = dspy.OutputField(
        desc="Generated report based on the operation performed. "
             "Can be one of 20+ different report types including: "
             "ConnectionReport, ToolDiscoveryReport, ToolExecutionReport, "
             "ErrorReport, PerformanceReport, SecurityReport, "
             "HealthCheckReport, BatchExecutionReport, ResourceUsageReport, "
             "AuditReport, ConfigurationReport, NetworkReport, "
             "DatabaseReport, FileOperationReport, GitOperationReport, "
             "SystemMonitorReport, WebScrapingReport, DataProcessingReport, "
             "DeploymentReport, SummaryReport, and more. "
             "All reports include tools_used field listing tools that were utilized."
    )