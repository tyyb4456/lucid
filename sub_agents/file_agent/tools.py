"""
LUCID File System Tools - Complete File System Control
Capabilities: System-wide file operations, search, bulk operations
"""

from langchain_core.tools import tool
from pathlib import Path
import shutil
import os
import glob
import json
from typing import Optional

@tool
def search_files(pattern: str, directory: str = "C:\\", max_results: int = 50) -> str:
    """
    Search for files ANYWHERE on the system by name pattern.
    
    Args:
        pattern: File name pattern (supports wildcards *, ?)
        directory: Starting directory (default: C:\\ - entire system)
        max_results: Maximum number of results to return
    
    Examples:
        pattern="*.docx", directory="C:\\Users"
        pattern="project*", directory="C:\\"
    """
    try:
        results = []
        search_path = Path(directory)
        
        # Use glob for pattern matching
        for file_path in search_path.rglob(pattern):
            if len(results) >= max_results:
                break
            results.append(str(file_path))
        
        if not results:
            return f"No files found matching '{pattern}' in {directory}"
        
        return f"Found {len(results)} file(s):\n" + "\n".join(results)
    
    except PermissionError:
        return f"Permission denied accessing {directory}"
    except Exception as e:
        return f"Error searching files: {e}"


@tool
def read_any_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read contents of ANY file on the system.
    
    Args:
        file_path: Absolute path to file
        encoding: File encoding (default: utf-8)
    
    Examples:
        "C:\\Users\\YourName\\Documents\\notes.txt"
        "C:\\Windows\\System32\\drivers\\etc\\hosts"
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        # Check file size (limit to 1MB for safety)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 1:
            return f"File too large ({size_mb:.2f}MB). Please specify a smaller file."
        
        content = path.read_text(encoding=encoding)
        
        # Limit output
        if len(content) > 5000:
            return f"File content (first 5000 chars):\n{content[:5000]}\n\n... [truncated]"
        
        return f"File content:\n{content}"
    
    except UnicodeDecodeError:
        return f"Cannot read file - appears to be binary. File: {file_path}"
    except PermissionError:
        return f"Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_any_file(file_path: str, content: str, mode: str = "w") -> str:
    """
    Write/create a file ANYWHERE on the system.
    
    Args:
        file_path: Absolute path where to create file
        content: Content to write
        mode: 'w' (overwrite) or 'a' (append)
    
    Examples:
        "C:\\Users\\YourName\\Desktop\\notes.txt"
    """
    try:
        path = Path(file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        if mode == "a":
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            path.write_text(content, encoding="utf-8")
        
        return f"File written successfully: {file_path}"
    
    except PermissionError:
        return f"Permission denied: {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def delete_any_file(file_path: str) -> str:
    """
    Delete ANY file on the system.
    
    Args:
        file_path: Absolute path to file to delete
    
    ⚠️ DANGEROUS - File will be permanently deleted!
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        # Safety check - don't delete system files
        system_paths = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]
        if any(str(path).startswith(sys_path) for sys_path in system_paths):
            return f"⚠️ SAFETY: Refusing to delete system file: {file_path}"
        
        path.unlink()
        return f"Deleted: {file_path}"
    
    except PermissionError:
        return f"Permission denied: {file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"


@tool
def move_file(source: str, destination: str) -> str:
    """
    Move/rename a file from one location to another.
    
    Args:
        source: Current file path
        destination: New file path
    """
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return f"Source file not found: {source}"
        
        # Create destination directory if needed
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src), str(dst))
        return f"Moved {source} → {destination}"
    
    except Exception as e:
        return f"Error moving file: {e}"


@tool
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file to a new location.
    
    Args:
        source: File to copy
        destination: Where to copy it
    """
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return f"Source file not found: {source}"
        
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(src), str(dst))
        return f"Copied {source} → {destination}"
    
    except Exception as e:
        return f"Error copying file: {e}"


@tool
def list_directory(directory: str = ".", show_hidden: bool = False) -> str:
    """
    List contents of any directory on the system.
    
    Args:
        directory: Path to directory
        show_hidden: Include hidden files
    """
    try:
        path = Path(directory)
        
        if not path.exists():
            return f"Directory not found: {directory}"
        
        if not path.is_dir():
            return f"Not a directory: {directory}"
        
        items = []
        for item in path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            size = ""
            if item.is_file():
                size_bytes = item.stat().st_size
                size = f" ({size_bytes / 1024:.1f} KB)" if size_bytes < 1024*1024 else f" ({size_bytes / (1024*1024):.1f} MB)"
            
            item_type = "📁" if item.is_dir() else "📄"
            items.append(f"{item_type} {item.name}{size}")
        
        if not items:
            return f"Directory is empty: {directory}"
        
        return f"Contents of {directory}:\n" + "\n".join(items[:100])  # Limit to 100 items
    
    except PermissionError:
        return f"Permission denied: {directory}"
    except Exception as e:
        return f"Error listing directory: {e}"


@tool
def get_file_info(file_path: str) -> str:
    """
    Get detailed information about a file (size, dates, permissions).
    
    Args:
        file_path: Path to file
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        stat = path.stat()
        
        import datetime
        created = datetime.datetime.fromtimestamp(stat.st_ctime)
        modified = datetime.datetime.fromtimestamp(stat.st_mtime)
        
        size_mb = stat.st_size / (1024 * 1024)
        
        info = f"""
📄 File Information: {path.name}

Path: {file_path}
Size: {size_mb:.2f} MB ({stat.st_size:,} bytes)
Created: {created.strftime('%Y-%m-%d %H:%M:%S')}
Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}
Type: {'Directory' if path.is_dir() else 'File'}
"""
        return info.strip()
    
    except Exception as e:
        return f"Error getting file info: {e}"


@tool
def create_directory(directory_path: str) -> str:
    """
    Create a new directory (including parent directories).
    
    Args:
        directory_path: Path to create
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return f"Directory created: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {e}"