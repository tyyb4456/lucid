from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    TodoListMiddleware,
    ContextEditingMiddleware, 
    ClearToolUsesEdit
)

from tools import (
    search_web,
    open_url,
    download_file,
    get_webpage_content,
    check_internet_connection,
    get_public_ip,
    ping_host,
    open_maps_location
)

tools = [
    search_web,
    open_url,
    download_file,
    get_webpage_content,
    check_internet_connection,
    get_public_ip,
    ping_host,
    open_maps_location
]

SYSTEM_PROMPT = """
You are LUCID, an expert Web & Network agent capable of browsing the internet, downloading files, and performing network diagnostics.

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
            "download_file": {"allowed_decisions": ["approve", "reject"]},
            "open_url": {"allowed_decisions": ["approve", "reject"]},
        }
    ),
    ModelFallbackMiddleware("gpt-5.4-mini", "claude-3-5-sonnet-20241022"),
    TodoListMiddleware(),
    ContextEditingMiddleware(edits=[ClearToolUsesEdit(trigger=100000, keep=3)]),
]

def web_agent():
    return {
        "name": "web_agent",
        "description": "Web Agent for internet browsing, searching, and network tools",
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
        "model": "gpt-5.4",
        "middleware": middleware,
    }
