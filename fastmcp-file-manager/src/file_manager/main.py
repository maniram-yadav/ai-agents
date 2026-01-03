"""
FastMCP File Manager Server
Provides tools for managing files and folders with grouping by extension.
"""
import os
import json
import shutil
import asyncio
import mimetypes
import hashlib
import humanize
import magic
from pathlib import Path
from typing import List,Dict,Any,Optional,Tuple
from datetime import datetime
from dataclasses import dataclass,asdict
from concurrent.futures import ThreadPoolExecutor

from fastmcp  import FastMCP
from pydantic import BaseModel,Field,validator

mcp = FastMCP("file-manager")

# Global thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=4 )

# Initialize mimetypes and magic
mimetypes.init()
magic_mime = magic.Magic(mime=True)

# ========== Pydantic Models ==========
class FileInfo(BaseModel):
    """Model for file information."""
    name: str
    path: str
    size: int
    size_human:str
    extension:str
    mime_type: str
    is_dir: bool
    created: str
    modified: str
    permissions: str
    parent: str

class FileGroup(BaseModel):
    """Model for grouped files by extension."""
    extension: str
    count: int
    total_size: int
    total_size_human: str
    files: List[FileInfo]

class FolderSummary(BaseModel):
    """Model for folder summary."""
    path: str
    total_files: int
    total_dirs: int
    total_size: int
    total_size_human: str
    extensions: Dict[str, int]
    largest_file: Optional[FileInfo] = None
    oldest_file: Optional[FileInfo] = None
    newest_file: Optional[FileInfo] = None

class SearchResult(BaseModel):
    """Model for search results."""
    path: str
    name: str
    is_dir: bool
    size: int
    size_human: str
    matches: List[str] = Field(default_factory=list)

class MoveRequest(BaseModel):
    """Model for move/copy operations."""
    source_path: str
    target_path: str
    overwrite: bool = False


class BatchOperation(BaseModel):
    """Model for batch operations."""
    file_paths: List[str]
    target_dir: str
    operation: str = Field(..., pattern="^(copy|move)$")

# ========== Helper Functions ==========

def get_file_info(filepath: Path) -> FileInfo:
    stat = filepath.stat()
    try :
        mime_type = magic_mime.from_file(str(filepath))
    except :
        mime_type = mimetypes.guess_type(str(filepath))[0] or "application/octet-stream"
    
    return FileInfo(
            name=filepath.name,
            path=str(filepath),
            size=stat.st_size,
            size_human=humanize.naturalsize(stat.st_size),
            extension=filepath.suffix.lower() if not filepath.is_dir() else "",
            mime_type=mime_type if not filepath.is_dir() else "inode/directory",
            is_dir=filepath.is_dir(),
            created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            permissions=oct(stat.st_mode)[-3:],
            parent=str(filepath.parent)
        )

async def run_in_executor(func, *args):
    """Run blocking function in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# ========== MCP Server Handlers ==========
