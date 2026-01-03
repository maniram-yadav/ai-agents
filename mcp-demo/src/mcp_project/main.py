import asyncio
import logging
from typing import Any
from mcp_project import mcp
from mcp import ClienSession,StdioServerParameters
from mcp.Server import Server
from mcp.server.models import (TextContent,Tool , Argument)

import mcp.server.stdio

server = Server("mcp-project");


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
     """Return available tools"""
     return [
         Tool(
             name="get_weather",
             description="Get curent weather for the location",
             inputSchema={
                 "type":"object",
                 "properties":{
                     "location":{
                         "type":"string",
                         "description":"City name"
                     }
                 },
                 "required":["location"]
             }
         )
     ]

@server.call_tool()
async def handle_call_tool(name:str,
                          arguments:dict[str,Any]|None) -> list[TextContent] :
    """Handle tool executions"""
    if name=="get_weather" :
        location = arguments["location"] if arguments else "unknown"
        return [
            TextContent(
                "type":"text",
                  "text":f"Weather in {location} : Sunday 72*F"
            )
        ]
    raise ValueError(f"unknown tool: {name}")

@server.list_resources()
async def handle_list_resources() -> list[dict]:
    """List available resources."""
    return [
        {
            "uri": "file:///example.txt",
            "name": "Example Resource",
            "description": "An example text resource",
            "mimeType": "text/plain"
        }
    ]

@server.read_resource()
async def handle_read_resource(uri:str) -> str:
    """Read resource content."""
    if uri=="file:///example.txt":
          return "This is example resource content."
    raise ValueError(f"Unknown resource: {uri}")

def main():
     """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    async with mcp.server.stdio.stdio_server() as (read_stream,write_stream):
        async with ClientSession(read_stream,write_stream,server_initialization_options={}) as session:
            await session.initialize()
            await server.run(session,read_stream,write_stream)
    print("Hello from mcp-demo!")


if __name__ == "__main__":
     asyncio.run(main())