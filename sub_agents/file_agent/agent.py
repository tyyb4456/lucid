from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    TodoListMiddleware,
    ContextEditingMiddleware, 
    ClearToolUsesEdit
)

from tools import (
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

SYSTEM_PROMPT = """
You are LUCID, an expert File System automation agent with full control over the user's files and directories.

## CORE BEHAVIOR
Think step-by-step before acting. For every task:
1. **Plan** – Break the task into ordered actions
2. **Execute** – Use tools one at a time, checking results
3. **Verify** – Confirm each step succeeded before continuing
4. **Report** – Summarize what was done and the final outcome
"""

middleware=[
    HumanInTheLoopMiddleware(
        interrupt_on={
            "delete_any_file": {"allowed_decisions": ["approve", "reject"]},
            "write_any_file": {"allowed_decisions": ["approve", "reject"]},
            "move_file": {"allowed_decisions": ["approve", "reject"]},
        }
    ),
    ModelFallbackMiddleware("gpt-5.4-mini", "claude-3-5-sonnet-20241022"),
    TodoListMiddleware(),
    ContextEditingMiddleware(edits=[ClearToolUsesEdit(trigger=100000, keep=3)]),
]

def file_agent():
    return {
        "name": "file_agent",
        "description": "File Agent for managing, reading, writing, and searching files",
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
        "model": "gpt-5.4",
        "middleware": middleware,
    }
