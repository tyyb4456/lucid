"""
LUCID File System Tools - Complete File System Control
Capabilities: System-wide file operations, search, bulk operations
"""

from langchain_core.tools import tool
from pathlib import Path
import shutil
import os
import json
import datetime
from typing import Optional


@tool
def search_files(pattern: str, directory: str = "C:\\Users", max_results: int = 50) -> str:
    """
    Search for files anywhere on the system by name pattern. Use this when the user
    wants to FIND a file but doesn't know or hasn't provided the full path.

    Use this tool when:
    - User says "find", "locate", "where is", "search for" a file
    - You need a file's full path before reading/writing/deleting it
    - User provides only a filename without a directory

    Args:
        pattern: File name or wildcard pattern to search for.
                 Supports * (any characters) and ? (single character).
                 Examples: "*.docx", "report_2024*", "notes.txt", "budget*.xlsx"
        directory: Root directory to start searching from.
                   Default is C:\\Users to cover all user files without scanning the entire OS.
                   Use "C:\\" only if you need a full system search.
        max_results: Maximum results to return (default 50, lower for faster results)

    Returns:
        A list of full absolute paths matching the pattern, with file sizes.
        Returns an error message if no files are found or access is denied.

    Examples:
        search_files("budget_2024.xlsx")                          → finds under C:\\Users
        search_files("*.log", "C:\\Users\\tayyab\\AppData")       → find log files
        search_files("resume*", "C:\\Users\\tayyab\\Documents")   → find resume files
    """
    try:
        results = []
        search_path = Path(directory)

        for file_path in search_path.rglob(pattern):
            if len(results) >= max_results:
                break
            try:
                size = file_path.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                results.append(f"{file_path}  [{size_str}]")
            except (PermissionError, OSError):
                results.append(str(file_path))

        if not results:
            return f"No files found matching '{pattern}' in {directory}. Try a broader pattern or different directory."

        output = f"Found {len(results)} file(s) matching '{pattern}':\n"
        output += "\n".join(results)
        if len(results) == max_results:
            output += f"\n\n⚠️ Result limit reached ({max_results}). Refine your pattern or reduce scope."
        return output

    except PermissionError:
        return f"Permission denied accessing {directory}. Try a subdirectory within C:\\Users."
    except Exception as e:
        return f"Error searching files: {e}"


@tool
def read_any_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read and return the full text content of a file. Use this when the user wants to
    VIEW, SHOW, DISPLAY, or CHECK the contents of a file.

    Use this tool when:
    - User says "read", "show", "open", "what's in", "display", "view" a file
    - You need to inspect a file's content before editing it
    - You need to verify a file was written correctly

    Do NOT use for binary files (images, executables, .zip, .pdf, .docx, etc.) —
    those will return garbage. Only use for plain text files: .txt, .log, .py,
    .json, .csv, .md, .html, .xml, .bat, .ps1, .ini, .cfg, .yaml, etc.

    Args:
        file_path: Full absolute Windows path to the file.
                   Example: "C:\\Users\\tayyab\\Desktop\\notes.txt"
        encoding: Text encoding. Use "utf-8" (default) for most files.
                  Try "cp1252" or "latin-1" if utf-8 fails on older Windows files.

    Returns:
        The file's text content (up to 5000 characters, truncated if larger).
        Returns an error if the file doesn't exist, is binary, or is too large.

    Examples:
        read_any_file("C:\\Users\\tayyab\\Desktop\\notes.txt")
        read_any_file("C:\\Users\\tayyab\\Documents\\config.json")
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return f"File not found: {file_path}\nTip: Use search_files() to locate it first."

        if not path.is_file():
            return f"'{file_path}' is a directory, not a file. Use list_directory() to browse it."

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 2:
            return (
                f"File is too large to read ({size_mb:.1f} MB): {file_path}\n"
                f"Only files under 2 MB can be read. Consider reading a specific section."
            )

        content = path.read_text(encoding=encoding, errors="replace")

        if len(content) > 5000:
            return (
                f"File content (first 5000 of {len(content)} characters):\n"
                f"{'─' * 40}\n{content[:5000]}\n{'─' * 40}\n"
                f"⚠️ File truncated. Full file has {len(content):,} characters."
            )

        return f"File content of '{path.name}':\n{'─' * 40}\n{content}\n{'─' * 40}"

    except UnicodeDecodeError:
        return (
            f"Cannot read '{file_path}' as text — it appears to be a binary file.\n"
            f"Only plain text files (.txt, .log, .py, .json, .csv, etc.) can be read with this tool."
        )
    except PermissionError:
        return f"Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_any_file(file_path: str, content: str, mode: str = "w") -> str:
    """
    Create a new file or write content to an existing file. This is how you save,
    create, or update any text-based file on the system.

    Use this tool when:
    - User says "create", "save", "write", "make a file", "generate a file"
    - User wants to save output (notes, a script, a report, a list) to disk
    - You need to update/overwrite an existing file's content
    - User says "append", "add to", "update" a file (use mode="a")

    IMPORTANT: If the user doesn't specify where to save, default to the Desktop.
    Always confirm the FULL path with the user after writing.

    Args:
        file_path: Full absolute Windows path where the file should be saved.
                   Examples:
                     "C:\\Users\\tayyab\\Desktop\\notes.txt"
                     "C:\\Users\\tayyab\\Documents\\report.md"
        content: The text content to write into the file. Can be any string.
        mode: Write mode:
              "w" = overwrite (create new or replace existing) — DEFAULT
              "a" = append (add to end of existing file without deleting current content)

    Returns:
        Success message with the full path and file size, or an error message.

    Examples:
        write_any_file("C:\\Users\\tayyab\\Desktop\\todo.txt", "1. Buy groceries\\n2. Call dentist")
        write_any_file("C:\\Users\\tayyab\\Desktop\\log.txt", "\\nNew entry added", mode="a")
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if mode == "a":
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            action = "Appended to"
        else:
            path.write_text(content, encoding="utf-8")
            action = "Created" if not path.exists() else "Overwritten"

        size_kb = path.stat().st_size / 1024
        return (
            f"✅ {action}: {file_path}\n"
            f"   Size: {size_kb:.1f} KB  |  Lines: {content.count(chr(10)) + 1}"
        )

    except PermissionError:
        return f"Permission denied: {file_path}\nTip: Make sure the directory exists and you have write access."
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def delete_any_file(file_path: str) -> str:
    """
    Permanently delete a file from the system. This action CANNOT be undone.

    Use this tool ONLY when:
    - User explicitly says "delete", "remove", "erase", "get rid of" a specific file
    - User has confirmed they want the file deleted

    ⚠️ DESTRUCTIVE OPERATION — The file will be permanently deleted (NOT moved to Recycle Bin).
    This tool requires human approval before execution (interrupt is enabled).
    NEVER call this without the user having clearly asked for deletion.

    Args:
        file_path: Full absolute Windows path to the file to delete.
                   Example: "C:\\Users\\tayyab\\Desktop\\old_notes.txt"

    Returns:
        Confirmation message with the deleted file path, or an error/refusal message.

    Safety rules (built-in):
    - Will REFUSE to delete anything inside C:\\Windows, C:\\Program Files, or C:\\Program Files (x86)
    - Will return an error if file doesn't exist
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return f"File not found (already deleted or wrong path): {file_path}"

        if not path.is_file():
            return f"'{file_path}' is a directory. Use a dedicated folder-deletion approach instead."

        # Safety: Block system directories
        protected = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData\\Microsoft",
        ]
        if any(str(path).lower().startswith(p.lower()) for p in protected):
            return f"🚫 BLOCKED: Refusing to delete system file: {file_path}"

        file_size = path.stat().st_size
        path.unlink()
        return (
            f"🗑️ Deleted: {file_path}\n"
            f"   Size freed: {file_size / 1024:.1f} KB"
        )

    except PermissionError:
        return f"Permission denied — cannot delete: {file_path}\nThe file may be open in another program."
    except Exception as e:
        return f"Error deleting file: {e}"


@tool
def move_file(source: str, destination: str) -> str:
    """
    Move a file from one location to another, or rename it.
    Moving a file to the same directory with a different name = rename.

    Use this tool when:
    - User says "move", "relocate", "transfer" a file to another folder
    - User says "rename" a file (move it to the same folder with a new name)
    - You need to organize files into folders

    Args:
        source: Full absolute path to the file you want to move.
                Example: "C:\\Users\\tayyab\\Desktop\\report.docx"
        destination: Full absolute path of the new location (including filename).
                     Example: "C:\\Users\\tayyab\\Documents\\Work\\report.docx"
                     To rename: "C:\\Users\\tayyab\\Desktop\\final_report.docx"

    Returns:
        Success message showing the move operation (source → destination), or an error.

    Notes:
        - Parent directories at the destination are created automatically if missing.
        - If a file already exists at destination, it will be overwritten.
    """
    try:
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return f"Source file not found: {source}\nTip: Use search_files() to confirm the path."

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

        return f"✅ Moved successfully:\n   From: {source}\n   To:   {destination}"

    except PermissionError:
        return f"Permission denied — check that neither file is open in another program."
    except Exception as e:
        return f"Error moving file: {e}"


@tool
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file to a new location, leaving the original intact.

    Use this tool when:
    - User says "copy", "duplicate", "backup", "make a copy of" a file
    - You want to create a backup before overwriting or editing a file
    - User wants the same file in multiple locations

    Args:
        source: Full absolute path to the file to copy.
                Example: "C:\\Users\\tayyab\\Documents\\notes.txt"
        destination: Full absolute path for the copied file (including filename).
                     Example: "C:\\Users\\tayyab\\Desktop\\notes_backup.txt"

    Returns:
        Success message showing source → destination copy, or an error message.

    Notes:
        - File metadata (timestamps) is preserved.
        - Parent directories at destination are created automatically if missing.
        - If destination already exists, it will be overwritten.
    """
    try:
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return f"Source file not found: {source}\nTip: Use search_files() to confirm the path."

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))

        size_kb = dst.stat().st_size / 1024
        return (
            f"✅ Copied successfully:\n"
            f"   From: {source}\n"
            f"   To:   {destination}\n"
            f"   Size: {size_kb:.1f} KB"
        )

    except PermissionError:
        return f"Permission denied — source file may be locked by another process."
    except Exception as e:
        return f"Error copying file: {e}"


@tool
def list_directory(directory: str, show_hidden: bool = False) -> str:
    """
    List all files and folders inside a directory. Use this to BROWSE or EXPLORE
    what's inside a folder before performing operations on its contents.

    Use this tool when:
    - User says "list", "show", "what's in", "browse" a folder
    - You need to see what files are in a directory before working with them
    - User wants to know the contents of Desktop, Documents, Downloads, etc.
    - You need to verify a file was created or moved to the right place

    Args:
        directory: Full absolute path to the folder to list.
                   Common shortcuts:
                     Desktop:   "C:\\Users\\tayyab\\Desktop"
                     Documents: "C:\\Users\\tayyab\\Documents"
                     Downloads: "C:\\Users\\tayyab\\Downloads"
        show_hidden: If True, includes files/folders starting with '.' (default False)

    Returns:
        A formatted list of files (📄) and folders (📁) with sizes, sorted folders-first.
        Returns an error if the path doesn't exist or is not a directory.
    """
    try:
        path = Path(directory)

        if not path.exists():
            return f"Directory not found: {directory}"

        if not path.is_file() is False and path.is_file():
            return f"'{directory}' is a file, not a directory. Use read_any_file() to read it."

        if not path.is_dir():
            return f"Not a directory: {directory}"

        dirs, files = [], []
        for item in path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            try:
                if item.is_dir():
                    dirs.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                    files.append(f"📄 {item.name}  [{size_str}]")
            except (PermissionError, OSError):
                continue

        dirs.sort()
        files.sort()
        items = dirs + files

        if not items:
            return f"Directory is empty: {directory}"

        header = f"📂 {directory}  ({len(dirs)} folders, {len(files)} files)\n{'─' * 50}\n"
        return header + "\n".join(items[:100]) + (
            f"\n\n⚠️ Showing first 100 of {len(items)} items." if len(items) > 100 else ""
        )

    except PermissionError:
        return f"Permission denied: {directory}"
    except Exception as e:
        return f"Error listing directory: {e}"


@tool
def get_file_info(file_path: str) -> str:
    """
    Get detailed metadata about a file: size, creation date, last modified date, and type.
    Use this when you need facts ABOUT a file rather than its contents.

    Use this tool when:
    - User asks "when was this file created/modified?", "how big is this file?"
    - User asks "does this file exist?", "what type is this file?"
    - You need to check if a file exists before reading or writing it
    - You want to verify a file operation completed successfully

    Args:
        file_path: Full absolute Windows path to the file or folder.
                   Example: "C:\\Users\\tayyab\\Desktop\\report.xlsx"

    Returns:
        A formatted summary including: full path, file size, creation date,
        last modified date, and file type. Returns an error if not found.
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return f"Not found: {file_path}\nUse search_files() to locate it."

        stat = path.stat()
        created = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

        size_bytes = stat.st_size
        if size_bytes < 1024:
            size_str = f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB ({size_bytes:,} bytes)"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB ({size_bytes:,} bytes)"

        ext = path.suffix.lower()
        file_type = "Directory" if path.is_dir() else f"File ({ext} format)" if ext else "File (no extension)"

        return (
            f"📄 {path.name}\n"
            f"{'─' * 40}\n"
            f"Full Path:     {file_path}\n"
            f"Type:          {file_type}\n"
            f"Size:          {size_str}\n"
            f"Created:       {created}\n"
            f"Last Modified: {modified}\n"
            f"Exists:        ✅ Yes"
        )

    except Exception as e:
        return f"Error getting file info: {e}"


@tool
def create_directory(directory_path: str) -> str:
    """
    Create a new folder (directory) at the specified path, including any missing parent folders.

    Use this tool when:
    - User says "create a folder", "make a directory", "set up a folder"
    - You need to organize files and the destination folder doesn't exist yet
    - You want to set up a project folder structure

    Args:
        directory_path: Full absolute Windows path for the new directory.
                        All missing parent folders will be created automatically.
                        Example: "C:\\Users\\tayyab\\Desktop\\ProjectX\\Assets\\Images"

    Returns:
        Success message confirming the directory was created, or an error message.
        If the directory already exists, returns a message confirming it's already there.
    """
    try:
        path = Path(directory_path)

        if path.exists():
            return f"Directory already exists: {directory_path}"

        path.mkdir(parents=True, exist_ok=True)
        return f"✅ Directory created: {directory_path}"

    except PermissionError:
        return f"Permission denied: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {e}"