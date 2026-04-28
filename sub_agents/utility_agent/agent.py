from .utility_tools import (
    get_current_datetime,
    calculate_math,
    timer_countdown,
    convert_units,
    create_json_file,
    read_json_file,
    get_weather,
    create_reminder,
    generate_password
)

tools = [
    get_current_datetime,
    calculate_math,
    timer_countdown,
    convert_units,
    create_json_file,
    read_json_file,
    get_weather,
    create_reminder,
    generate_password
]

from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """
You are LUCID, an expert Utility agent equipped with a suite of everyday tools for calculations, conversions, and miscellaneous tasks.

## CORE BEHAVIOR
Think step-by-step before acting. For every task:
1. **Plan** – Break the task into ordered actions
2. **Execute** – Use tools one at a time, checking results
3. **Verify** – Confirm each step succeeded before continuing
4. **Report** – Summarize what was done and the final outcome
"""

def utility_agent():
    return {
        "name": "utility_agent",
        "description": "Utility Agent for math, time, weather, and miscellaneous tasks",
        "system_prompt": SYSTEM_PROMPT,
        "tools": tools,
    }
