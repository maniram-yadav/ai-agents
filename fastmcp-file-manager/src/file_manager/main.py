"""
FastMCP File Manager Server
Provides tools for managing files and folders with grouping by extension.
"""
import os
import json
import shutil
import hashlib
import mimetypes
import magic
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import humanize

from fastmcp import FastMCP
from pydantic import BaseModel, Field, validator

# Initialize FastMCP app
mcp = FastMCP("file-manager")

# Global thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=10)

# Initialize mimetypes and magic
mimetypes.init()
magic_mime = magic.Magic(mime=True)

# ========== Pydantic Models ==========

class FileInfo(BaseModel):
    """Model for file information."""
    name: str
    path: str
    size: int
    size_human: str
    extension: str
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
    """Get detailed information about a file."""
    stat = filepath.stat()
    try:
        mime_type = magic_mime.from_file(str(filepath))
    except:
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

# ========== MCP Tools ==========

@mcp.tool()
async def list_files_and_folders(
    folder_path: str = Field(..., description="Path to the folder to list"),
    recursive: bool = Field(False, description="List files recursively"),
    group_by_extension: bool = Field(True, description="Group files by extension"),
    include_hidden: bool = Field(False, description="Include hidden files/folders"),
    sort_by: str = Field("name", description="Sort by: name, size, modified, created"),
    sort_order: str = Field("asc", description="Sort order: asc or desc")
) -> Dict[str, Any]:
    """
    List all files and folders in a directory with optional grouping by extension.
    
    Args:
        folder_path: Path to the folder to analyze
        recursive: Whether to list files recursively
        group_by_extension: Group files by their extensions
        include_hidden: Include hidden files and folders
        sort_by: Sort files by name, size, modified, or created
        sort_order: Ascending or descending order
    
    Returns:
        Dictionary containing files, folders, and grouped data
    """
    try:
        folder = Path(folder_path).expanduser().resolve()
        
        if not folder.exists():
            return {"error": f"Folder not found: {folder_path}"}
        if not folder.is_dir():
            return {"error": f"Path is not a directory: {folder_path}"}
        
        all_files = []
        all_dirs = []
        file_groups = {}
        
        # Walk through directory
        walk_func = folder.rglob if recursive else folder.glob
        pattern = "*" if include_hidden else "[!.]*"
        
        for path in walk_func(pattern):
            if not include_hidden and any(part.startswith('.') for part in path.parts):
                continue
                
            if path.is_dir():
                all_dirs.append(get_file_info(path))
            else:
                file_info = get_file_info(path)
                all_files.append(file_info)
                
                if group_by_extension:
                    ext = file_info.extension or "no_extension"
                    if ext not in file_groups:
                        file_groups[ext] = []
                    file_groups[ext].append(file_info)
        
        # Sort files
        reverse = sort_order.lower() == "desc"
        if sort_by == "name":
            all_files.sort(key=lambda x: x.name.lower(), reverse=reverse)
            all_dirs.sort(key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == "size":
            all_files.sort(key=lambda x: x.size, reverse=reverse)
        elif sort_by == "modified":
            all_files.sort(key=lambda x: x.modified, reverse=reverse)
        elif sort_by == "created":
            all_files.sort(key=lambda x: x.created, reverse=reverse)
        
        # Prepare grouped data
        grouped_data = []
        if group_by_extension:
            for ext, files in file_groups.items():
                total_size = sum(f.size for f in files)
                grouped_data.append(FileGroup(
                    extension=ext,
                    count=len(files),
                    total_size=total_size,
                    total_size_human=humanize.naturalsize(total_size),
                    files=sorted(files, key=lambda x: x.name.lower())
                ))
            grouped_data.sort(key=lambda x: x.count, reverse=True)
        
        # Prepare summary
        total_size = sum(f.size for f in all_files)
        extensions_count = {}
        for file in all_files:
            ext = file.extension or "no_extension"
            extensions_count[ext] = extensions_count.get(ext, 0) + 1
        
        summary = FolderSummary(
            path=str(folder),
            total_files=len(all_files),
            total_dirs=len(all_dirs),
            total_size=total_size,
            total_size_human=humanize.naturalsize(total_size),
            extensions=extensions_count,
            largest_file=max(all_files, key=lambda x: x.size) if all_files else None,
            oldest_file=min(all_files, key=lambda x: x.created) if all_files else None,
            newest_file=max(all_files, key=lambda x: x.created) if all_files else None
        )
        
        return {
            "success": True,
            "folder": str(folder),
            "summary": summary.dict(),
            "files": [f.dict() for f in all_files],
            "folders": [d.dict() for d in all_dirs],
            "grouped_by_extension": [g.dict() for g in grouped_data] if group_by_extension else [],
            "total_items": len(all_files) + len(all_dirs)
        }
        
    except Exception as e:
        return {"error": f"Failed to list files: {str(e)}"}

@mcp.tool()
async def create_folder(
    folder_path: str = Field(..., description="Path of the folder to create"),
    parents: bool = Field(True, description="Create parent directories if they don't exist"),
    exist_ok: bool = Field(False, description="Don't raise error if folder already exists")
) -> Dict[str, Any]:
    """
    Create a new folder.
    
    Args:
        folder_path: Path where the folder should be created
        parents: Create parent directories if needed
        exist_ok: Don't error if folder already exists
    
    Returns:
        Operation result with folder info
    """
    try:
        folder = Path(folder_path).expanduser().resolve()
        
        if folder.exists() and not exist_ok:
            return {"error": f"Folder already exists: {folder_path}"}
        
        await run_in_executor(folder.mkdir, parents, exist_ok)
        
        return {
            "success": True,
            "message": f"Folder created: {folder_path}",
            "folder_info": get_file_info(folder).dict()
        }
        
    except Exception as e:
        return {"error": f"Failed to create folder: {str(e)}"}

@mcp.tool()
async def delete_path(
    path: str = Field(..., description="Path to delete (file or folder)"),
    recursive: bool = Field(False, description="Delete folders recursively"),
    force: bool = Field(False, description="Force deletion even if readonly")
) -> Dict[str, Any]:
    """
    Delete a file or folder.
    
    Args:
        path: Path to the file or folder to delete
        recursive: Delete folders and their contents
        force: Force deletion even if readonly
    
    Returns:
        Operation result
    """
    try:
        target = Path(path).expanduser().resolve()
        
        if not target.exists():
            return {"error": f"Path not found: {path}"}
        
        if force and target.exists():
            await run_in_executor(lambda p: p.chmod(0o777), target)
        
        if target.is_dir():
            if not recursive:
                return {"error": "Cannot delete folder without recursive=True"}
            await run_in_executor(shutil.rmtree, str(target))
        else:
            await run_in_executor(target.unlink)
        
        return {
            "success": True,
            "message": f"Deleted: {path}",
            "type": "folder" if target.is_dir() else "file"
        }
        
    except Exception as e:
        return {"error": f"Failed to delete: {str(e)}"}

@mcp.tool()
async def move_file(
    source_path: str = Field(..., description="Source file/folder path"),
    target_path: str = Field(..., description="Destination path"),
    overwrite: bool = Field(False, description="Overwrite if destination exists")
) -> Dict[str, Any]:
    """
    Move or rename a file or folder.
    
    Args:
        source_path: Path to the file/folder to move
        target_path: Destination path
        overwrite: Overwrite if destination exists
    
    Returns:
        Operation result
    """
    try:
        source = Path(source_path).expanduser().resolve()
        target = Path(target_path).expanduser().resolve()
        
        if not source.exists():
            return {"error": f"Source not found: {source_path}"}
        
        if target.exists() and not overwrite:
            return {"error": f"Target exists: {target_path}. Use overwrite=True to overwrite."}
        
        await run_in_executor(shutil.move, str(source), str(target))
        
        return {
            "success": True,
            "message": f"Moved {source_path} to {target_path}",
            "source": get_file_info(source).dict() if source.exists() else None,
            "destination": get_file_info(target).dict()
        }
        
    except Exception as e:
        return {"error": f"Failed to move file: {str(e)}"}

@mcp.tool()
async def copy_file(
    source_path: str = Field(..., description="Source file/folder path"),
    target_path: str = Field(..., description="Destination path"),
    overwrite: bool = Field(False, description="Overwrite if destination exists")
) -> Dict[str, Any]:
    """
    Copy a file or folder.
    
    Args:
        source_path: Path to the file/folder to copy
        target_path: Destination path
        overwrite: Overwrite if destination exists
    
    Returns:
        Operation result
    """
    try:
        source = Path(source_path).expanduser().resolve()
        target = Path(target_path).expanduser().resolve()
        
        if not source.exists():
            return {"error": f"Source not found: {source_path}"}
        
        if target.exists() and not overwrite:
            return {"error": f"Target exists: {target_path}. Use overwrite=True to overwrite."}
        
        if source.is_dir():
            await run_in_executor(shutil.copytree, str(source), str(target), dirs_exist_ok=overwrite)
        else:
            await run_in_executor(shutil.copy2, str(source), str(target))
        
        return {
            "success": True,
            "message": f"Copied {source_path} to {target_path}",
            "source": get_file_info(source).dict(),
            "destination": get_file_info(target).dict()
        }
        
    except Exception as e:
        return {"error": f"Failed to copy file: {str(e)}"}

@mcp.tool()
async def search_files(
    search_path: str = Field(..., description="Path to search in"),
    name_pattern: Optional[str] = Field(None, description="Filename pattern (supports wildcards)"),
    content_search: Optional[str] = Field(None, description="Text to search in file contents"),
    extension: Optional[str] = Field(None, description="File extension filter"),
    min_size: Optional[int] = Field(None, description="Minimum file size in bytes"),
    max_size: Optional[int] = Field(None, description="Maximum file size in bytes"),
    recursive: bool = Field(True, description="Search recursively"),
    case_sensitive: bool = Field(False, description="Case sensitive search")
) -> Dict[str, Any]:
    """
    Search for files with various criteria.
    
    Args:
        search_path: Root directory to search
        name_pattern: Filename pattern with wildcards (*, ?)
        content_search: Text to search in file contents
        extension: Filter by file extension
        min_size: Minimum file size
        max_size: Maximum file size
        recursive: Search subdirectories
        case_sensitive: Case sensitive matching
    
    Returns:
        Search results
    """
    try:
        search_dir = Path(search_path).expanduser().resolve()
        
        if not search_dir.exists() or not search_dir.is_dir():
            return {"error": f"Invalid search path: {search_path}"}
        
        results = []
        walk_func = search_dir.rglob if recursive else search_dir.glob
        pattern = name_pattern or "*"
        
        for path in walk_func(pattern):
            if path.is_dir():
                continue
            
            # Extension filter
            if extension and not str(path).lower().endswith(extension.lower()):
                continue
            
            # Size filters
            stat = path.stat()
            if min_size is not None and stat.st_size < min_size:
                continue
            if max_size is not None and stat.st_size > max_size:
                continue
            
            matches = []
            
            # Content search
            if content_search:
                try:
                    content = await run_in_executor(path.read_text, encoding='utf-8', errors='ignore')
                    search_text = content_search if case_sensitive else content_search.lower()
                    file_content = content if case_sensitive else content.lower()
                    
                    if search_text in file_content:
                        # Find all occurrences
                        start = 0
                        while True:
                            pos = file_content.find(search_text, start)
                            if pos == -1:
                                break
                            context_start = max(0, pos - 20)
                            context_end = min(len(file_content), pos + len(search_text) + 20)
                            matches.append(f"...{file_content[context_start:context_end]}...")
                            start = pos + 1
                            if len(matches) >= 5:  # Limit matches per file
                                break
                except:
                    pass
            
            if content_search and not matches:
                continue
            
            results.append(SearchResult(
                path=str(path),
                name=path.name,
                is_dir=False,
                size=stat.st_size,
                size_human=humanize.naturalsize(stat.st_size),
                matches=matches
            ))
        
        return {
            "success": True,
            "search_path": str(search_dir),
            "total_results": len(results),
            "results": [r.dict() for r in results],
            "criteria": {
                "name_pattern": name_pattern,
                "content_search": content_search,
                "extension": extension,
                "min_size": min_size,
                "max_size": max_size
            }
        }
        
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

@mcp.tool()
async def get_file_stats(
    file_path: str = Field(..., description="Path to the file")
) -> Dict[str, Any]:
    """
    Get detailed statistics about a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Detailed file statistics
    """
    try:
        file = Path(file_path).expanduser().resolve()
        
        if not file.exists():
            return {"error": f"File not found: {file_path}"}
        if file.is_dir():
            return {"error": f"Path is a directory, not a file: {file_path}"}
        
        stat = file.stat()
        
        # Calculate MD5 hash
        def calculate_md5():
            hash_md5 = hashlib.md5()
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        md5_hash = await run_in_executor(calculate_md5)
        
        # Try to get line count
        try:
            line_count = await run_in_executor(lambda: sum(1 for _ in open(file, 'r', encoding='utf-8', errors='ignore')))
        except:
            line_count = None
        
        # Get encoding guess
        try:
            import chardet
            rawdata = await run_in_executor(lambda: open(file, 'rb').read(10000))
            encoding = chardet.detect(rawdata)['encoding']
        except:
            encoding = None
        
        return {
            "success": True,
            "file_info": get_file_info(file).dict(),
            "statistics": {
                "md5_hash": md5_hash,
                "line_count": line_count,
                "encoding_guess": encoding,
                "inode": stat.st_ino,
                "device": stat.st_dev,
                "hard_links": stat.st_nlink,
                "user_id": stat.st_uid,
                "group_id": stat.st_gid,
                "access_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "change_time": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get file stats: {str(e)}"}

@mcp.tool()
async def batch_operations(
    operations: List[Dict[str, Any]] = Field(..., description="List of operations to perform")
) -> Dict[str, Any]:
    """
    Perform batch operations on files.
    
    Args:
        operations: List of operation objects with type and parameters
    
    Returns:
        Batch operation results
    """
    try:
        results = []
        
        for op in operations:
            op_type = op.get("type")
            params = op.get("params", {})
            
            if op_type == "copy":
                result = await copy_file(**params)
            elif op_type == "move":
                result = await move_file(**params)
            elif op_type == "delete":
                result = await delete_path(**params)
            elif op_type == "create_folder":
                result = await create_folder(**params)
            else:
                result = {"error": f"Unknown operation type: {op_type}"}
            
            results.append({
                "type": op_type,
                "params": params,
                "result": result
            })
        
        # Count successes
        success_count = sum(1 for r in results if r["result"].get("success"))
        
        return {
            "success": True,
            "total_operations": len(results),
            "successful_operations": success_count,
            "failed_operations": len(results) - success_count,
            "operations": results
        }
        
    except Exception as e:
        return {"error": f"Batch operations failed: {str(e)}"}

@mcp.tool()
async def organize_by_extension(
    source_dir: str = Field(..., description="Source directory to organize"),
    target_dir: Optional[str] = Field(None, description="Target directory (defaults to source)"),
    create_subfolders: bool = Field(True, description="Create subfolders for each extension"),
    move_files: bool = Field(False, description="Move files instead of copying"),
    dry_run: bool = Field(False, description="Show what would be done without actually doing it")
) -> Dict[str, Any]:
    """
    Organize files by their extensions into subfolders.
    
    Args:
        source_dir: Directory containing files to organize
        target_dir: Where to organize files (defaults to source)
        create_subfolders: Create folders for each extension
        move_files: Move files instead of copying
        dry_run: Preview changes without executing
    
    Returns:
        Organization plan or results
    """
    try:
        source = Path(source_dir).expanduser().resolve()
        target = Path(target_dir).expanduser().resolve() if target_dir else source
        
        if not source.exists() or not source.is_dir():
            return {"error": f"Invalid source directory: {source_dir}"}
        
        # Scan files
        files = []
        for path in source.rglob("*"):
            if path.is_file():
                files.append(get_file_info(path))
        
        # Group by extension
        extension_groups = {}
        for file in files:
            ext = file.extension.lstrip('.') if file.extension else "no_extension"
            if ext not in extension_groups:
                extension_groups[ext] = []
            extension_groups[ext].append(file)
        
        # Create organization plan
        plan = []
        total_files = 0
        
        for ext, ext_files in extension_groups.items():
            if create_subfolders:
                target_folder = target / ext
            else:
                target_folder = target
            
            for file in ext_files:
                source_path = Path(file.path)
                target_path = target_folder / source_path.name
                
                operation = {
                    "source": str(source_path),
                    "destination": str(target_path),
                    "extension": ext,
                    "operation": "move" if move_files else "copy",
                    "would_create_folder": create_subfolders and not target_folder.exists()
                }
                plan.append(operation)
                total_files += 1
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "total_files": total_files,
                "unique_extensions": len(extension_groups),
                "plan": plan,
                "summary": {
                    "source": str(source),
                    "target": str(target),
                    "create_subfolders": create_subfolders,
                    "move_files": move_files
                }
            }
        
        # Execute operations
        results = []
        for op in plan:
            source_path = Path(op["source"])
            target_path = Path(op["destination"])
            
            # Create target folder if needed
            if op["would_create_folder"]:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform operation
            try:
                if op["operation"] == "move":
                    shutil.move(str(source_path), str(target_path))
                else:
                    shutil.copy2(str(source_path), str(target_path))
                results.append({
                    **op,
                    "success": True
                })
            except Exception as e:
                results.append({
                    **op,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "dry_run": False,
            "total_files": total_files,
            "successful_operations": success_count,
            "failed_operations": len(results) - success_count,
            "results": results,
            "extension_summary": {ext: len(files) for ext, files in extension_groups.items()}
        }
        
    except Exception as e:
        return {"error": f"Organization failed: {str(e)}"}

# ========== Resource Providers ==========

@mcp.resource("file://stats/{path}")
def get_file_statistics_resource(path: str) -> str:
    """Resource endpoint for file statistics."""
    import json
    stats = asyncio.run(get_file_stats(path))
    return json.dumps(stats, indent=2)

@mcp.resource("file://list/{path}")
def list_directory_resource(path: str) -> str:
    """Resource endpoint for directory listing."""
    import json
    listing = asyncio.run(list_files_and_folders(path, recursive=False))
    return json.dumps(listing, indent=2)

# ========== Main Entry Point ==========
def main():
    """Main function to run the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Run the MCP server
    main()