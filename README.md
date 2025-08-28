# Enhanced MCP Server Manager with 20 Useful Server Configurations

A comprehensive Python toolkit for managing multiple MCP (Model Context Protocol) servers with proper resource management, error handling, and 20 pre-configured useful servers that require no API keys.

## 🚀 Quick Start

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Check prerequisites and list available servers
python install_servers.py --check
python install_servers.py --list

# Install a basic set of servers
python install_servers.py --example basic_setup
```

### Basic Usage with Configuration

```python
import asyncio
from mcp_config_loader import MCPConfigLoader

# Load configuration and create manager
loader = MCPConfigLoader()
manager = loader.create_manager_from_example("basic_setup")

# Use context manager for automatic cleanup
async with manager.managed_connection():
    tools = await manager.tools()
    print(f"Found {len(tools)} tools from {len(manager)} servers")
    
    # Execute a tool
    result = await manager.execute_tool("tool_name", **args)
```

## 📦 20 Pre-configured MCP Servers (No API Keys Required)

### File & System Management
- **filesystem**: File operations, directory listing, read/write files
- **git**: Git repository operations, status, log, diff, commit
- **shell**: Safe shell command execution
- **system_monitor**: CPU, memory, disk usage monitoring

### Data Processing
- **sqlite**: SQLite database operations and queries
- **csv_processor**: CSV file processing and analysis
- **json_processor**: JSON validation and transformation
- **yaml_processor**: YAML file processing
- **text_processor**: Text search, replace, analysis

### Web & Network
- **fetch**: HTTP requests and web content fetching
- **puppeteer**: Web scraping and browser automation
- **network_tools**: Ping, traceroute, port scanning

### Development Tools
- **docker**: Container management and operations
- **kubernetes**: K8s cluster management
- **log_analyzer**: Log file analysis and parsing
- **markdown_processor**: Markdown processing and conversion

### Utilities
- **time**: Time operations and timezone conversions
- **memory**: Persistent memory storage
- **postgres**: PostgreSQL database operations (local)
- **brave_search**: Web search (free tier available)

## 🎯 Usage Examples

### Predefined Setups

```python
from mcp_config_loader import MCPConfigLoader

loader = MCPConfigLoader()

# Basic development setup
manager = loader.create_manager_from_example("basic_setup")

# Data analysis setup
manager = loader.create_manager_from_example("data_analysis_setup")

# Web automation setup
manager = loader.create_manager_from_example("web_automation_setup")

# DevOps setup
manager = loader.create_manager_from_example("devops_setup")
```

### Custom Server Selection

```python
# Select specific servers
manager = loader.create_custom_manager([
    "filesystem", "git", "sqlite", "time"
])

# Select by category
manager = loader.create_manager_from_category("data_processing")
```

## 🛠 Installation Options

### Using the Installer Script

```bash
# Install servers for a specific use case
python install_servers.py --example development_setup

# Install servers by category
python install_servers.py --category data_processing

# Install specific servers
python install_servers.py --servers filesystem git sqlite

# Install all Node.js servers
python install_servers.py --all-node

# Install all Python servers
python install_servers.py --all-python
```

### Manual Installation

```bash
# Node.js-based servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-sqlite

# Python-based servers (examples - actual packages may vary)
pip install mcp-server-shell
pip install mcp-server-docker
pip install mcp-server-json
```

## 📋 Key Improvements from Original Code

### 1. **Fixed Critical Bugs**
- ✅ Fixed dictionary syntax error in `tools()` method
- ✅ Added proper resource management and cleanup
- ✅ Comprehensive error handling

### 2. **Enhanced Functionality**
- 🔧 `get_tool_by_name()`: Find specific tools
- 🔧 `execute_tool()`: Direct tool execution
- 🔧 Context manager for automatic cleanup
- 🔧 Enhanced tool information with server tracking

### 3. **Configuration Management**
- 📝 JSON-based server configurations
- 📝 Predefined usage examples
- 📝 Category-based organization
- 📝 Installation automation

### 4. **Developer Experience**
- 📚 Comprehensive documentation
- 📚 Type hints throughout
- 📚 Logging integration
- 📚 Example scripts and tests

## 🏗 Project Structure

```
/workspace/
├── mcp_server_manager.py          # Enhanced main class
├── mcp_config_loader.py           # Configuration management
├── mcp_servers_config.json        # 20 server configurations
├── install_servers.py             # Installation helper
├── example_usage.py               # Usage examples
├── test_mcp_manager.py            # Basic tests
├── test_with_example_server.py    # Integration tests
├── example_mcp_server.py          # Example server for testing
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── FIXES_AND_ENHANCEMENTS.md     # Technical details
```

## 🔒 Security Considerations

- **shell**: Can execute arbitrary commands - use with caution
- **docker**: Requires Docker daemon access
- **kubernetes**: Requires kubectl configuration
- **filesystem**: Can read/write files - restrict directories appropriately
- **network_tools**: Can perform network operations

## 🧪 Testing

```bash
# Test the enhanced manager
python test_mcp_manager.py

# Test with example server
python test_with_example_server.py

# Run usage examples
python example_usage.py
```

## 📖 Configuration File

The `mcp_servers_config.json` file contains:
- 20 useful MCP server configurations
- Installation commands for each server type
- Predefined usage examples
- Security considerations
- Server categorization

## 🤝 Contributing

1. Add new server configurations to `mcp_servers_config.json`
2. Update installation commands as needed
3. Add tests for new functionality
4. Update documentation

## 📄 License

This project enhances the original MCP Server Manager with comprehensive improvements and configurations for practical use.