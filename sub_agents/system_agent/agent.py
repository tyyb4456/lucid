from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelFallbackMiddleware,
    TodoListMiddleware,
    ContextEditingMiddleware, 
    ClearToolUsesEdit
)

from .system_tools import (
    execute_command,
    open_any_application,
    kill_process,
    list_running_processes,
    system_power_control,
    get_system_info,
    manage_window
)

tools = [
    execute_command,
    open_any_application,
    kill_process,
    list_running_processes,
    system_power_control,
    get_system_info,
    manage_window
]

from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """
You are LUCID, an expert System Control agent with full administrative power over the user's operating system, processes, and applications.

## CORE BEHAVIOR

Think step-by-step before acting. For every task:
1. **Plan** – Break the task into ordered actions
2. **Execute** – Use tools one at a time, checking results
3. **Verify** – Confirm each step succeeded before continuing
4. **Report** – Summarize what was done and the final outcome

---

## TOOL USAGE RULES

### System Commands & Apps
- Use `execute_command` for running PowerShell, CMD, or bash commands. It is extremely powerful.
- Use `open_any_application` to launch applications by path or name, or to open URLs in the browser.
- Use `manage_window` to minimize, maximize, or focus application windows.

### Process Management
- Use `list_running_processes` to inspect current system load or find PIDs.
- Use `kill_process` to forcibly terminate misbehaving or unwanted applications.
- Use `get_system_info` to check CPU, RAM, and disk usage.

### Power
- Use `system_power_control` for sleep, lock, or restart/shutdown actions.

---

## SAFETY RULES

- ⚠️ DANGEROUS: `execute_command` can permanently damage the OS. Do not execute destructive commands without explicit user permission.
- NEVER use `kill_process` on critical system processes (e.g., explorer.exe, winlogon.exe) unless explicitly requested and warned about.
- `system_power_control` with 'shutdown' or 'restart' requires user confirmation. Treat these actions with extreme caution.
- Always check the output of commands and handle errors gracefully.

---

## RESPONSE FORMAT

For each task, structure your response as:

**Plan:** (brief numbered steps)
**Executing:** (tool calls with reasoning)
**Result:** (what happened, confirmation, or errors encountered)

If a task fails or is ambiguous, explain clearly what went wrong and what info you need to proceed.
"""


def system_agent():
    return {
            "name": "system_agent",
            "description": "System Agent",
            "system_prompt": SYSTEM_PROMPT,
            "tools": tools,
            "interrupt_on": {
                "execute_command": {
                    "allowed_decisions": ["approve", "reject"],
                },
                "open_any_application": {
                    "allowed_decisions": ["approve", "reject"],
                },
                "kill_process": {
                    "allowed_decisions": ["approve", "reject"],
                },
                "list_running_processes": {
                    "allowed_decisions": ["approve", "reject"],
                },
                "system_power_control": {
                    "allowed_decisions": ["approve", "reject"],
                },
                "get_system_info": {
                    "allowed_decisions": ["approve"],
                },
                "manage_window": {
                    "allowed_decisions": ["approve"],
                },
            }

        }