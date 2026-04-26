from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    TodoListMiddleware,
    ContextEditingMiddleware, 
    ClearToolUsesEdit
)

from tools import (
    add_todo,
    read_todos,
    complete_todo,
    delete_todo,
    clear_completed_todos,
    create_note,
    read_notes,
    delete_note
)

tools = [
    add_todo,
    read_todos,
    complete_todo,
    delete_todo,
    clear_completed_todos,
    create_note,
    read_notes,
    delete_note
]

SYSTEM_PROMPT = """
You are LUCID, an expert Productivity agent designed to manage tasks, notes, and workflows efficiently.

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
            "delete_todo": {"allowed_decisions": ["approve", "reject"]},
            "clear_completed_todos": {"allowed_decisions": ["approve", "reject"]},
            "delete_note": {"allowed_decisions": ["approve", "reject"]},
        }
    ),
    ModelFallbackMiddleware("gpt-5.4-mini", "claude-3-5-sonnet-20241022"),
    TodoListMiddleware(),
    ContextEditingMiddleware(edits=[ClearToolUsesEdit(trigger=100000, keep=3)]),
]

def productivity_agent():
    return {
        "name": "productivity_agent",
        "description": "Productivity Agent for managing notes and tasks",
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
        "model": "gpt-5.4",
        "middleware": middleware,
    }