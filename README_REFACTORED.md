# Enhanced MCP Server Manager - Refactored Architecture

A completely refactored, modular MCP (Model Context Protocol) server management system with clean separation of concerns, Pydantic models, environment-based configuration, and a single DSPy signature for flexible operations.

## 🏗️ Architecture Overview

The system has been completely refactored into separate, focused modules:

```
📁 Enhanced MCP Server Manager/
├── 🔧 models.py          # 20+ Pydantic models with validation
├── ⚙️ config.py          # Environment & JSON configuration management  
├── 🤖 mcpman.py          # Core MCP Manager agent
├── 📝 sig.py             # Single DSPy signature definition
├── 🚀 main.py            # Main application with try/except/finally
├── 📋 mcp_servers_config.json  # 20 server configurations
├── 🌍 .env.example       # Environment configuration template
└── 🧪 test_refactored.py # Architecture validation tests
```

## 🎯 Key Architectural Improvements

### 1. **Modular Design with Separation of Concerns**
- **models.py**: All Pydantic models and type definitions
- **config.py**: Configuration management with environment variables
- **mcpman.py**: Core MCP Manager business logic
- **sig.py**: Single DSPy signature for all operations
- **main.py**: Application entry point with proper error handling

### 2. **Flexible Input/Output System**
- **Single Input**: `BaseRequest` model that accepts any fields through `**kwargs` at runtime
- **Union Output**: 20+ different report types based on operation performed
- **Runtime Flexibility**: Add new fields to requests without code changes

### 3. **Comprehensive Pydantic Models**
```python
# 20+ Report Types Available
ReportOutput = Union[
    ConnectionReport,           # Server connection results
    ToolDiscoveryReport,       # Tool discovery results  
    ToolExecutionReport,       # Tool execution results
    ErrorReport,               # Error conditions
    PerformanceReport,         # Performance metrics
    SecurityReport,            # Security validations
    HealthCheckReport,         # System health status
    BatchExecutionReport,      # Batch operations
    ResourceUsageReport,       # Resource monitoring
    AuditReport,              # Audit trails
    ConfigurationReport,       # Configuration changes
    NetworkReport,            # Network operations
    DatabaseReport,           # Database operations
    FileOperationReport,      # File system operations
    GitOperationReport,       # Git operations
    SystemMonitorReport,      # System monitoring
    WebScrapingReport,        # Web scraping results
    DataProcessingReport,     # Data processing results
    DeploymentReport,         # Deployment operations
    SummaryReport,            # Operation summaries
    # ... and more
]
```

### 4. **Environment-Based Configuration**
```bash
# .env file configuration
LOG_LEVEL=INFO
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
ALLOWED_COMMANDS=filesystem,git,sqlite,time,memory,fetch
RESTRICTED_PATHS=/etc,/root,/sys,/proc
ENABLE_SHELL_COMMANDS=false
CACHE_ENABLED=true
DEBUG_MODE=false
```

### 5. **Agent-Based Architecture**
```python
# Single signature handles all operations
class MCPManagerSignature(dspy.Signature):
    request: BaseRequest = dspy.InputField(desc="Flexible request model")
    report: ReportOutput = dspy.OutputField(desc="Union of 20+ report types")

# Agent processes requests in try/except/finally structure
class MCPManagerAgent(dspy.Module):
    def forward(self, request: BaseRequest) -> ReportOutput:
        # Determines operation type and generates appropriate report
```

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit configuration as needed
nano .env
```

### Basic Usage
```python
from models import BaseRequest
from main import MCPManagerAgent
from mcpman import MCPManager
from config import config_manager

# Create agent
mcp_manager = MCPManager(config_manager)
agent = MCPManagerAgent(mcp_manager)

# Flexible request - accepts any fields at runtime
request = BaseRequest(
    operation="connect",
    server_names=["filesystem", "git"],
    custom_field="any_value",
    timeout=60
)

# Process request - returns appropriate report type
report = agent.forward(request)
print(f"Operation: {report.report_type}")
print(f"Success: {report.success}")
print(f"Tools used: {len(report.tools_used)}")
```

### Command Line Usage
```bash
# Run main application
python main.py

# Run in interactive mode
python main.py --interactive

# Use custom config file
python main.py --config custom_config.json

# Test architecture
python test_refactored.py
```

## 🔧 Configuration Management

### Environment Configuration
The system uses Pydantic Settings for environment-based configuration:

```python
class EnvironmentConfig(BaseSettings):
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    default_timeout: int = Field(default=30, env="DEFAULT_TIMEOUT")
    allowed_commands: str = Field(env="ALLOWED_COMMANDS")
    # ... automatic environment variable binding
```

### Server Configuration
20 pre-configured MCP servers in JSON format:
```json
{
  "mcp_servers": [
    {
      "name": "filesystem",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "category": "file_management",
      "enabled": true
    }
  ]
}
```

## 🤖 Agent Operations

The agent supports multiple operation types through a single signature:

### Connection Operations
```python
request = BaseRequest(operation="connect", server_names=["filesystem"])
report = agent.forward(request)  # Returns ConnectionReport
```

### Tool Discovery
```python
request = BaseRequest(operation="discover")
report = agent.forward(request)  # Returns ToolDiscoveryReport
```

### Tool Execution
```python
request = BaseRequest(
    operation="execute",
    tool_name="list_files",
    tool_args={"path": "/workspace"}
)
report = agent.forward(request)  # Returns ToolExecutionReport
```

### Performance Monitoring
```python
request = BaseRequest(operation="performance")
report = agent.forward(request)  # Returns PerformanceReport
```

## 📊 Report System

All operations generate comprehensive reports with:
- **Execution metrics**: Time, success/failure, error details
- **Tools used**: Complete list of tools utilized in the operation
- **Type-specific data**: Relevant information for each report type
- **Metadata**: Request ID, timestamp, additional context

### Example Report Structure
```python
{
    "report_type": "tool_execution_report",
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "execute_tool_123",
    "tools_used": [
        {
            "name": "list_files",
            "server_name": "filesystem",
            "execution_time": 0.5,
            "status": "success"
        }
    ],
    "execution_time": 0.5,
    "success": true,
    "result": ["file1.txt", "file2.txt"]
}
```

## 🔒 Security Features

- **Command validation**: Only allowed commands can be executed
- **Path restrictions**: Prevent access to sensitive directories
- **Shell command control**: Optional shell command execution
- **Input validation**: Pydantic models validate all inputs
- **Error handling**: Comprehensive error reporting without exposure

## 🧪 Testing

### Architecture Validation
```bash
python test_refactored.py
```

Tests verify:
- ✅ Configuration loading and validation
- ✅ Pydantic model functionality
- ✅ MCP Manager operations
- ✅ DSPy signature definition
- ✅ Agent integration
- ✅ Report type generation
- ✅ Error handling

### Manual Testing
```bash
# Interactive mode for manual testing
python main.py --interactive
```

## 📈 Performance Features

- **Async operations**: Full async/await support
- **Connection pooling**: Efficient server connection management
- **Caching**: Optional tool and result caching
- **Metrics collection**: Performance monitoring and reporting
- **Resource tracking**: Memory and connection usage monitoring

## 🔄 Migration from Original

The refactored version maintains compatibility while adding:

1. **Modular architecture** instead of monolithic design
2. **Pydantic validation** instead of manual validation
3. **Environment configuration** instead of hardcoded values
4. **Single signature** instead of multiple interfaces
5. **Comprehensive reporting** instead of basic outputs
6. **Agent-based processing** instead of direct function calls

## 🤝 Contributing

1. **Add new report types**: Extend the `ReportOutput` union in `models.py`
2. **Add new operations**: Extend the agent's `forward()` method in `main.py`
3. **Add new servers**: Update `mcp_servers_config.json`
4. **Add new configuration**: Extend `EnvironmentConfig` in `config.py`

## 📄 License

Enhanced MCP Server Manager with comprehensive refactoring for production use.

---

## 🎯 Summary of Refactoring

This refactored version transforms the original monolithic MCP Server Manager into a clean, modular, production-ready system with:

- **5 focused modules** with clear responsibilities
- **20+ Pydantic models** with comprehensive validation
- **Single DSPy signature** handling all operations
- **Flexible I/O system** accepting any runtime fields
- **Environment-based configuration** for deployment flexibility
- **Agent-based architecture** with proper error handling
- **Comprehensive reporting** with 20+ report types
- **Production-ready features** including security, performance monitoring, and testing

The system maintains all original functionality while providing a much cleaner, more maintainable, and extensible architecture.