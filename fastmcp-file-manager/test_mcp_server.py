"""
Test cases for FastMCP File Manager Server (stdio mode)
These tests demonstrate how to interact with the MCP server via JSON-RPC over stdio.
"""

import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path
import time

class MCPClient:
    """Simple MCP client for testing stdio transport."""

    def __init__(self, server_cmd):
        self.server_cmd = server_cmd
        self.process = None

    def start_server(self):
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            self.server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=os.getcwd()  # Add cwd
        )
        # Give server time to start
        time.sleep(0.1)

    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

    def send_request(self, method, params=None, id=1):
        """Send a JSON-RPC request to the server."""
        request = {
            "jsonrpc": "2.0",
            "id": id,
            "method": method,
            "params": params or {}
        }

        if self.process and self.process.stdin:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()

            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
        return None

def test_list_files_and_folders():
    """Test the list_files_and_folders tool."""
    print("=== Testing list_files_and_folders ===")

    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        (temp_path / "test.txt").write_text("Hello World")
        (temp_path / "script.py").write_text("print('test')")
        (temp_path / "data.json").write_text('{"key": "value"}')

        # Create subdirectory
        subdir = temp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested file")

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test basic listing
            response = client.send_request("tools/call", {
                "name": "list_files_and_folders",
                "arguments": {
                    "folder_path": str(temp_path),
                    "recursive": False,
                    "group_by_extension": True
                }
            })

            print("Basic listing response:")
            print(json.dumps(response, indent=2))

            # Test recursive listing
            response = client.send_request("tools/call", {
                "name": "list_files_and_folders",
                "arguments": {
                    "folder_path": str(temp_path),
                    "recursive": True,
                    "group_by_extension": False
                }
            })

            print("Recursive listing response:")
            print(json.dumps(response, indent=2))

            # Test with sorting
            response = client.send_request("tools/call", {
                "name": "list_files_and_folders",
                "arguments": {
                    "folder_path": str(temp_path),
                    "sort_by": "size",
                    "sort_order": "desc"
                }
            })

            print("Size-sorted listing response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_file_operations():
    """Test file operation tools."""
    print("=== Testing file operations ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test create_folder
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            # Test create_folder
            response = client.send_request("tools/call", {
                "name": "create_folder",
                "arguments": {
                    "folder_path": str(temp_path / "new_folder"),
                    "parents": True
                }
            })
            print("Create folder response:")
            print(json.dumps(response, indent=2))

            # Test copy_file
            response = client.send_request("tools/call", {
                "name": "copy_file",
                "arguments": {
                    "source_path": str(test_file),
                    "target_path": str(temp_path / "new_folder" / "copied.txt")
                }
            })
            print("Copy file response:")
            print(json.dumps(response, indent=2))

            # Test move_file
            response = client.send_request("tools/call", {
                "name": "move_file",
                "arguments": {
                    "source_path": str(temp_path / "new_folder" / "copied.txt"),
                    "target_path": str(temp_path / "moved.txt")
                }
            })
            print("Move file response:")
            print(json.dumps(response, indent=2))

            # Test get_file_stats
            response = client.send_request("tools/call", {
                "name": "get_file_stats",
                "arguments": {
                    "file_path": str(temp_path / "moved.txt")
                }
            })
            print("File stats response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_search_files():
    """Test the search_files tool."""
    print("=== Testing search_files ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with content
        (temp_path / "python_file.py").write_text("def hello():\n    print('Hello World')\n    return 'test'")
        (temp_path / "readme.txt").write_text("This is a README file with some text content.")
        (temp_path / "data.json").write_text('{"message": "Hello World", "status": "test"}')

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test filename pattern search
            response = client.send_request("tools/call", {
                "name": "search_files",
                "arguments": {
                    "search_path": str(temp_path),
                    "name_pattern": "*.py"
                }
            })
            print("Filename pattern search response:")
            print(json.dumps(response, indent=2))

            # Test content search
            response = client.send_request("tools/call", {
                "name": "search_files",
                "arguments": {
                    "search_path": str(temp_path),
                    "content_search": "Hello World"
                }
            })
            print("Content search response:")
            print(json.dumps(response, indent=2))

            # Test extension filter
            response = client.send_request("tools/call", {
                "name": "search_files",
                "arguments": {
                    "search_path": str(temp_path),
                    "extension": ".json"
                }
            })
            print("Extension filter search response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_batch_operations():
    """Test batch operations."""
    print("=== Testing batch_operations ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        (temp_path / "file1.txt").write_text("content1")
        (temp_path / "file2.txt").write_text("content2")

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test batch copy operations
            operations = [
                {
                    "type": "copy",
                    "params": {
                        "source_path": str(temp_path / "file1.txt"),
                        "target_path": str(temp_path / "copy1.txt")
                    }
                },
                {
                    "type": "copy",
                    "params": {
                        "source_path": str(temp_path / "file2.txt"),
                        "target_path": str(temp_path / "copy2.txt")
                    }
                },
                {
                    "type": "create_folder",
                    "params": {
                        "folder_path": str(temp_path / "batch_folder")
                    }
                }
            ]

            response = client.send_request("tools/call", {
                "name": "batch_operations",
                "arguments": {
                    "operations": operations
                }
            })
            print("Batch operations response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_organize_by_extension():
    """Test organize_by_extension tool."""
    print("=== Testing organize_by_extension ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with different extensions
        (temp_path / "doc1.txt").write_text("text document 1")
        (temp_path / "doc2.txt").write_text("text document 2")
        (temp_path / "script1.py").write_text("print('hello')")
        (temp_path / "script2.py").write_text("print('world')")
        (temp_path / "data.json").write_text('{"key": "value"}')

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test dry run first
            response = client.send_request("tools/call", {
                "name": "organize_by_extension",
                "arguments": {
                    "source_dir": str(temp_path),
                    "dry_run": True
                }
            })
            print("Organize dry run response:")
            print(json.dumps(response, indent=2))

            # Test actual organization
            response = client.send_request("tools/call", {
                "name": "organize_by_extension",
                "arguments": {
                    "source_dir": str(temp_path),
                    "move_files": False  # Copy instead of move
                }
            })
            print("Organize by extension response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_resources():
    """Test resource endpoints."""
    print("=== Testing resources ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test file
        test_file = temp_path / "test.txt"
        test_file.write_text("test content")

        client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
        client.start_server()

        try:
            # Test file stats resource
            response = client.send_request("resources/read", {
                "uri": f"file://stats/{test_file}"
            })
            print("File stats resource response:")
            print(json.dumps(response, indent=2))

            # Test directory listing resource
            response = client.send_request("resources/read", {
                "uri": f"file://list/{temp_path}"
            })
            print("Directory listing resource response:")
            print(json.dumps(response, indent=2))

        finally:
            client.stop_server()

def test_error_handling():
    """Test error handling scenarios."""
    print("=== Testing error handling ===")

    client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
    client.start_server()

    try:
        # Test non-existent path
        response = client.send_request("tools/call", {
            "name": "list_files_and_folders",
            "arguments": {
                "folder_path": "/non/existent/path"
            }
        })
        print("Non-existent path error response:")
        print(json.dumps(response, indent=2))

        # Test invalid tool name
        response = client.send_request("tools/call", {
            "name": "non_existent_tool",
            "arguments": {}
        })
        print("Invalid tool error response:")
        print(json.dumps(response, indent=2))

        # Test invalid resource URI
        response = client.send_request("resources/read", {
            "uri": "file://invalid/resource"
        })
        print("Invalid resource error response:")
        print(json.dumps(response, indent=2))

    finally:
        client.stop_server()

def test_initialization():
    """Test server initialization and tool listing."""
    print("=== Testing server initialization ===")

    client = MCPClient(["uv", "run", "file_manager_cli", "serve"])
    client.start_server()

    try:
        # Test tools/list
        response = client.send_request("tools/list")
        print("Tools list response:")
        print(json.dumps(response, indent=2))

        # Test resources/list
        response = client.send_request("resources/list")
        print("Resources list response:")
        print(json.dumps(response, indent=2))

        # Test initialize
        response = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        print("Initialize response:")
        print(json.dumps(response, indent=2))

    finally:
        client.stop_server()

if __name__ == "__main__":
    print("Running MCP File Manager Server Test Suite")
    print("=" * 50)

    # Run all tests
    test_initialization()
    test_list_files_and_folders()
    test_file_operations()
    test_search_files()
    test_batch_operations()
    test_organize_by_extension()
    test_resources()
    test_error_handling()

    print("=" * 50)
    print("Test suite completed!")