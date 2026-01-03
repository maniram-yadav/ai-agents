#!/usr/bin/env python3
"""Run the MCP server directly."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent.resolve()))
from mcp_project.main import main
if __name__ == "__main__":
    asyncio.run(main())
    