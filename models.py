"""
Base models for MCP Server Manager using Pydantic.

This module defines all the data models used throughout the application,
including input/output models, report types, and configuration models.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from mcp import StdioServerParameters


class ServerStatus(str, Enum):
    """Server connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


class ToolExecutionStatus(str, Enum):
    """Tool execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ReportType(str, Enum):
    """Types of reports that can be generated."""
    CONNECTION_REPORT = "connection_report"
    TOOL_DISCOVERY_REPORT = "tool_discovery_report"
    TOOL_EXECUTION_REPORT = "tool_execution_report"
    SERVER_STATUS_REPORT = "server_status_report"
    ERROR_REPORT = "error_report"
    PERFORMANCE_REPORT = "performance_report"
    SECURITY_REPORT = "security_report"
    HEALTH_CHECK_REPORT = "health_check_report"
    BATCH_EXECUTION_REPORT = "batch_execution_report"
    RESOURCE_USAGE_REPORT = "resource_usage_report"
    AUDIT_REPORT = "audit_report"
    CONFIGURATION_REPORT = "configuration_report"
    NETWORK_REPORT = "network_report"
    DATABASE_REPORT = "database_report"
    FILE_OPERATION_REPORT = "file_operation_report"
    GIT_OPERATION_REPORT = "git_operation_report"
    SYSTEM_MONITOR_REPORT = "system_monitor_report"
    WEB_SCRAPING_REPORT = "web_scraping_report"
    DATA_PROCESSING_REPORT = "data_processing_report"
    DEPLOYMENT_REPORT = "deployment_report"
    SUMMARY_REPORT = "summary_report"


# Base Models
class BaseRequest(BaseModel):
    """Base request model that accepts any additional fields at runtime."""
    model_config = ConfigDict(extra="allow")
    
    request_id: str = Field(default_factory=lambda: f"req_{datetime.now().timestamp()}")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)


class ToolInfo(BaseModel):
    """Information about a discovered or used tool."""
    name: str
    description: str = ""
    server_index: int
    server_name: str = ""
    input_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    capabilities: List[str] = Field(default_factory=list)
    execution_time: Optional[float] = None
    status: Optional[ToolExecutionStatus] = None
    error_message: Optional[str] = None


class ServerInfo(BaseModel):
    """Information about an MCP server."""
    name: str
    command: str
    args: List[str]
    status: ServerStatus = ServerStatus.DISCONNECTED
    connection_time: Optional[datetime] = None
    last_error: Optional[str] = None
    tool_count: int = 0
    response_time: Optional[float] = None


# Report Base Class
class BaseReport(BaseModel):
    """Base class for all report types."""
    report_type: ReportType
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str
    tools_used: List[ToolInfo] = Field(default_factory=list)
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Specific Report Types
class ConnectionReport(BaseReport):
    """Report for server connection operations."""
    report_type: Literal[ReportType.CONNECTION_REPORT] = ReportType.CONNECTION_REPORT
    servers_connected: List[ServerInfo] = Field(default_factory=list)
    servers_failed: List[ServerInfo] = Field(default_factory=list)
    total_servers: int = 0
    connection_success_rate: float = 0.0


class ToolDiscoveryReport(BaseReport):
    """Report for tool discovery operations."""
    report_type: Literal[ReportType.TOOL_DISCOVERY_REPORT] = ReportType.TOOL_DISCOVERY_REPORT
    discovered_tools: List[ToolInfo] = Field(default_factory=list)
    tools_by_server: Dict[str, List[ToolInfo]] = Field(default_factory=dict)
    total_tools: int = 0
    categories: List[str] = Field(default_factory=list)


class ToolExecutionReport(BaseReport):
    """Report for tool execution operations."""
    report_type: Literal[ReportType.TOOL_EXECUTION_REPORT] = ReportType.TOOL_EXECUTION_REPORT
    tool_name: str
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    execution_status: ToolExecutionStatus = ToolExecutionStatus.PENDING
    server_name: str = ""


class ServerStatusReport(BaseReport):
    """Report for server status checks."""
    report_type: Literal[ReportType.SERVER_STATUS_REPORT] = ReportType.SERVER_STATUS_REPORT
    servers: List[ServerInfo] = Field(default_factory=list)
    healthy_servers: int = 0
    unhealthy_servers: int = 0
    average_response_time: float = 0.0


class ErrorReport(BaseReport):
    """Report for error conditions."""
    report_type: Literal[ReportType.ERROR_REPORT] = ReportType.ERROR_REPORT
    error_type: str
    error_details: str
    stack_trace: Optional[str] = None
    affected_servers: List[str] = Field(default_factory=list)
    recovery_actions: List[str] = Field(default_factory=list)


class PerformanceReport(BaseReport):
    """Report for performance metrics."""
    report_type: Literal[ReportType.PERFORMANCE_REPORT] = ReportType.PERFORMANCE_REPORT
    avg_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    resource_usage: Dict[str, float] = Field(default_factory=dict)


class SecurityReport(BaseReport):
    """Report for security-related operations."""
    report_type: Literal[ReportType.SECURITY_REPORT] = ReportType.SECURITY_REPORT
    security_checks: List[Dict[str, Any]] = Field(default_factory=list)
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_status: Dict[str, bool] = Field(default_factory=dict)
    risk_level: Literal["low", "medium", "high", "critical"] = "low"


class HealthCheckReport(BaseReport):
    """Report for health check operations."""
    report_type: Literal[ReportType.HEALTH_CHECK_REPORT] = ReportType.HEALTH_CHECK_REPORT
    overall_health: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    component_health: Dict[str, str] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class BatchExecutionReport(BaseReport):
    """Report for batch tool execution operations."""
    report_type: Literal[ReportType.BATCH_EXECUTION_REPORT] = ReportType.BATCH_EXECUTION_REPORT
    batch_id: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    operation_results: List[Dict[str, Any]] = Field(default_factory=list)


class ResourceUsageReport(BaseReport):
    """Report for resource usage monitoring."""
    report_type: Literal[ReportType.RESOURCE_USAGE_REPORT] = ReportType.RESOURCE_USAGE_REPORT
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_usage: float = 0.0
    active_connections: int = 0


class AuditReport(BaseReport):
    """Report for audit trail operations."""
    report_type: Literal[ReportType.AUDIT_REPORT] = ReportType.AUDIT_REPORT
    audit_events: List[Dict[str, Any]] = Field(default_factory=list)
    user_actions: List[Dict[str, Any]] = Field(default_factory=list)
    system_changes: List[Dict[str, Any]] = Field(default_factory=list)


class ConfigurationReport(BaseReport):
    """Report for configuration operations."""
    report_type: Literal[ReportType.CONFIGURATION_REPORT] = ReportType.CONFIGURATION_REPORT
    current_config: Dict[str, Any] = Field(default_factory=dict)
    config_changes: List[Dict[str, Any]] = Field(default_factory=list)
    validation_results: Dict[str, bool] = Field(default_factory=dict)


class NetworkReport(BaseReport):
    """Report for network operations."""
    report_type: Literal[ReportType.NETWORK_REPORT] = ReportType.NETWORK_REPORT
    network_tests: List[Dict[str, Any]] = Field(default_factory=list)
    connectivity_status: Dict[str, str] = Field(default_factory=dict)
    latency_metrics: Dict[str, float] = Field(default_factory=dict)


class DatabaseReport(BaseReport):
    """Report for database operations."""
    report_type: Literal[ReportType.DATABASE_REPORT] = ReportType.DATABASE_REPORT
    database_operations: List[Dict[str, Any]] = Field(default_factory=list)
    query_performance: Dict[str, float] = Field(default_factory=dict)
    connection_pool_status: Dict[str, int] = Field(default_factory=dict)


class FileOperationReport(BaseReport):
    """Report for file system operations."""
    report_type: Literal[ReportType.FILE_OPERATION_REPORT] = ReportType.FILE_OPERATION_REPORT
    file_operations: List[Dict[str, Any]] = Field(default_factory=list)
    files_processed: int = 0
    bytes_transferred: int = 0
    operation_type: str = ""


class GitOperationReport(BaseReport):
    """Report for Git operations."""
    report_type: Literal[ReportType.GIT_OPERATION_REPORT] = ReportType.GIT_OPERATION_REPORT
    git_operations: List[Dict[str, Any]] = Field(default_factory=list)
    repository_status: Dict[str, Any] = Field(default_factory=dict)
    commits_processed: int = 0


class SystemMonitorReport(BaseReport):
    """Report for system monitoring operations."""
    report_type: Literal[ReportType.SYSTEM_MONITOR_REPORT] = ReportType.SYSTEM_MONITOR_REPORT
    system_metrics: Dict[str, float] = Field(default_factory=dict)
    process_info: List[Dict[str, Any]] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)


class WebScrapingReport(BaseReport):
    """Report for web scraping operations."""
    report_type: Literal[ReportType.WEB_SCRAPING_REPORT] = ReportType.WEB_SCRAPING_REPORT
    urls_processed: List[str] = Field(default_factory=list)
    data_extracted: Dict[str, Any] = Field(default_factory=dict)
    scraping_metrics: Dict[str, float] = Field(default_factory=dict)


class DataProcessingReport(BaseReport):
    """Report for data processing operations."""
    report_type: Literal[ReportType.DATA_PROCESSING_REPORT] = ReportType.DATA_PROCESSING_REPORT
    data_sources: List[str] = Field(default_factory=list)
    processing_steps: List[Dict[str, Any]] = Field(default_factory=list)
    output_metrics: Dict[str, Any] = Field(default_factory=dict)


class DeploymentReport(BaseReport):
    """Report for deployment operations."""
    report_type: Literal[ReportType.DEPLOYMENT_REPORT] = ReportType.DEPLOYMENT_REPORT
    deployment_steps: List[Dict[str, Any]] = Field(default_factory=list)
    deployment_status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    rollback_available: bool = False


class SummaryReport(BaseReport):
    """Summary report aggregating multiple operations."""
    report_type: Literal[ReportType.SUMMARY_REPORT] = ReportType.SUMMARY_REPORT
    operation_summary: Dict[str, int] = Field(default_factory=dict)
    performance_summary: Dict[str, float] = Field(default_factory=dict)
    error_summary: Dict[str, int] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


# Union type for all possible report outputs
ReportOutput = Union[
    ConnectionReport,
    ToolDiscoveryReport,
    ToolExecutionReport,
    ServerStatusReport,
    ErrorReport,
    PerformanceReport,
    SecurityReport,
    HealthCheckReport,
    BatchExecutionReport,
    ResourceUsageReport,
    AuditReport,
    ConfigurationReport,
    NetworkReport,
    DatabaseReport,
    FileOperationReport,
    GitOperationReport,
    SystemMonitorReport,
    WebScrapingReport,
    DataProcessingReport,
    DeploymentReport,
    SummaryReport
]


# Configuration Models
class ServerConfig(BaseModel):
    """Configuration for an individual MCP server."""
    name: str
    description: str = ""
    command: str
    args: List[str]
    category: str = "general"
    capabilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    security_note: Optional[str] = None
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 3


class MCPManagerConfig(BaseModel):
    """Main configuration for the MCP Manager."""
    servers: List[ServerConfig] = Field(default_factory=list)
    default_timeout: int = 30
    max_retries: int = 3
    connection_pool_size: int = 10
    tool_timeout: int = 60
    max_concurrent_tools: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 300
    debug_mode: bool = False
    log_level: str = "INFO"
    security_settings: Dict[str, Any] = Field(default_factory=dict)
    performance_settings: Dict[str, Any] = Field(default_factory=dict)