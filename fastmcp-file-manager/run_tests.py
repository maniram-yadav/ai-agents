#!/usr/bin/env python3
"""
Simple test runner for MCP File Manager Server
Run individual test functions or all tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from test_mcp_server import *

def run_single_test(test_name):
    """Run a single test function."""
    test_functions = {
        'init': test_initialization,
        'list': test_list_files_and_folders,
        'operations': test_file_operations,
        'search': test_search_files,
        'batch': test_batch_operations,
        'organize': test_organize_by_extension,
        'resources': test_resources,
        'errors': test_error_handling,
    }

    if test_name in test_functions:
        print(f"Running test: {test_name}")
        test_functions[test_name]()
    else:
        print(f"Unknown test: {test_name}")
        print("Available tests:", list(test_functions.keys()))

def main():
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        run_single_test(test_name)
    else:
        # Run all tests
        print("Running all tests...")
        test_initialization()
        test_list_files_and_folders()
        test_file_operations()
        test_search_files()
        test_batch_operations()
        test_organize_by_extension()
        test_resources()
        test_error_handling()

if __name__ == "__main__":
    main()