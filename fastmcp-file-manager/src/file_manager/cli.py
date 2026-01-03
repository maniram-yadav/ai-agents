"""CLI interface for the file manager."""
import argparse
import json
import sys
import asyncio
from pathlib import Path
from .main import mcp, list_files_and_folders, get_file_stats, search_files

def cli():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="File Manager MCP Server CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List files and folders")
    list_parser.add_argument("path", help="Directory path")
    list_parser.add_argument("--recursive", "-r", action="store_true", help="List recursively")
    list_parser.add_argument("--group", "-g", action="store_true", help="Group by extension")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get file statistics")
    stats_parser.add_argument("path", help="File path")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search files")
    search_parser.add_argument("path", help="Search directory")
    search_parser.add_argument("--pattern", "-p", help="Filename pattern")
    search_parser.add_argument("--content", "-c", help="Search content")
    search_parser.add_argument("--extension", "-e", help="File extension")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], 
                             help="Transport protocol")
    
    args = parser.parse_args()
    
    if args.command == "list":
        result = asyncio.run(list_files_and_folders.fn(
            folder_path=args.path,
            recursive=args.recursive,
            group_by_extension=args.group,
            include_hidden=False,
            sort_by="name",
            sort_order="asc"
        ))
        print(json.dumps(result, indent=2))
        
    elif args.command == "stats":
        result = asyncio.run(get_file_stats.fn(args.path))
        print(json.dumps(result, indent=2))
        
    elif args.command == "search":
        result = asyncio.run(search_files.fn(
            search_path=args.path,
            name_pattern=args.pattern,
            content_search=args.content,
            extension=args.extension
        ))
        print(json.dumps(result, indent=2))
        
    elif args.command == "serve":
        mcp.run(transport=args.transport)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()