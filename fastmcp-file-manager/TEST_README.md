# MCP File Manager Server - Test Suite

This directory contains comprehensive test cases for the FastMCP File Manager Server running in stdio mode.

## Test Files

- `test_mcp_server.py` - Complete test suite with MCP client implementation
- `run_tests.py` - Test runner script for executing individual or all tests

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Individual Tests
```bash
# Test server initialization and tool listing
python run_tests.py init

# Test file listing functionality
python run_tests.py list

# Test file operations (create, copy, move, delete)
python run_tests.py operations

# Test file search functionality
python run_tests.py search

# Test batch operations
python run_tests.py batch

# Test file organization by extension
python run_tests.py organize

# Test resource endpoints
python run_tests.py resources

# Test error handling scenarios
python run_tests.py errors
```

### Manual Testing with CLI

You can also test the server manually using the CLI:

```bash
# Start the MCP server
uv run file_manager_cli serve

# In another terminal, test with CLI commands
uv run file_manager_cli list /home/maniram/workspace/python/ai-agents/fastmcp-file-manager --group
uv run file_manager_cli stats /home/maniram/workspace/python/ai-agents/fastmcp-file-manager/pyproject.toml
uv run file_manager_cli search /home/maniram/workspace/python/ai-agents/fastmcp-file-manager --pattern "*.py"
```

## Test Coverage

The test suite covers:

1. **Server Initialization**
   - Tool listing
   - Resource listing
   - Protocol initialization

2. **File Operations**
   - List files and folders with various options
   - Create, copy, move, and delete files/folders
   - Get detailed file statistics

3. **Search Functionality**
   - Search by filename patterns
   - Content search within files
   - Extension-based filtering
   - Size-based filtering

4. **Batch Operations**
   - Multiple operations in a single request
   - Error handling in batch operations

5. **File Organization**
   - Organize files by extension
   - Dry-run mode for planning
   - Copy vs move operations

6. **Resource Endpoints**
   - File statistics via URI
   - Directory listings via URI

7. **Error Handling**
   - Invalid paths
   - Permission errors
   - Invalid tool/resource requests

## MCP Protocol

The tests use the Model Context Protocol (MCP) over stdio transport with JSON-RPC 2.0 messages:

- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `resources/list` - List available resources
- `resources/read` - Read a resource
- `initialize` - Initialize the connection

## Test Structure

Each test:
1. Creates temporary test files/directories
2. Starts an MCP server process
3. Sends JSON-RPC requests via stdin
4. Validates responses from stdout
5. Cleans up test files and stops the server

## Dependencies

The tests require:
- Python 3.10+
- uv package manager
- The fastmcp-file-manager package installed</content>
<parameter name="filePath">/home/maniram/workspace/python/ai-agents/fastmcp-file-manager/TEST_README.md