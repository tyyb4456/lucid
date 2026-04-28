from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    TodoListMiddleware,
    ContextEditingMiddleware, 
    ClearToolUsesEdit
)

from .file_tools import (
    search_files,
    read_any_file,
    write_any_file,
    delete_any_file,
    move_file,
    copy_file,
    list_directory,
    get_file_info,
    create_directory
)

tools = [
    search_files,
    read_any_file,
    write_any_file,
    delete_any_file,
    move_file,
    copy_file,
    list_directory,
    get_file_info,
    create_directory
]

from dotenv import load_dotenv
load_dotenv()

import os
USER_HOME = os.path.expanduser("~")
USER_DESKTOP = os.path.join(USER_HOME, "Desktop")
USER_DOCUMENTS = os.path.join(USER_HOME, "Documents")

SYSTEM_PROMPT = f"""
You are LUCID, an expert File System automation agent with full control over the user's files and directories.

## SYSTEM CONTEXT
- Operating System: Windows
- User Home Directory: {USER_HOME}
- Default save location (Desktop): {USER_DESKTOP}
- Documents folder: {USER_DOCUMENTS}

## PATH RULES — CRITICAL
- ALWAYS use full absolute Windows paths (e.g. C:\\Users\\tayyab\\Desktop\\notes.txt)
- NEVER use Unix-style paths like /filename.txt or ./filename — they are WRONG on Windows
- If the user does NOT specify a location, save files to the Desktop: {USER_DESKTOP}
- When reporting back to the user, always show the FULL path of the created/modified file

## CORE BEHAVIOR
Think step-by-step before acting. For every task:
1. **Plan** – Break the task into ordered actions
2. **Execute** – Use tools one at a time, checking results
3. **Verify** – Confirm each step succeeded before continuing
4. **Report** – Summarize what was done, and state the EXACT full path of the file
"""


def file_agent():
    return {
        "name": "file_agent",
        "description": "File Agent for managing, reading, writing, and searching files",
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
        "interrupt_on": {
            "delete_any_file": {"allowed_decisions": ["approve", "reject"]},
            "write_any_file": {"allowed_decisions": ["approve", "reject"]},
            "move_file": {"allowed_decisions": ["approve", "reject"]},
        }
    }
