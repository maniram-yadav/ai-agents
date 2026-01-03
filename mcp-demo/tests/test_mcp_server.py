"""Tests for MCP server."""
import pytest
import asyncio
from mcp_project.main import server


@pytest.mark.asyncio
async def test_list_tools():
    """Test tool listing."""
    tools = await server.list_tools()
    assert len(tools) > 0
    assert any(tool.name == "get_weather" for tool in tools)

@pytest.mark.asyncio
async def test_call_tool():
    """Test tool execution."""
    result = await server.call_tool(
        name="get_weather",
        arguments={"location": "New York"}
    )
    assert len(result) > 0
    assert "New York" in result[0].text