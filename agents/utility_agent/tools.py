"""
LUCID Utility Tools - Time, date, calculations, data management
"""

from langchain_core.tools import tool
import datetime
import json
from pathlib import Path
from typing import Optional

@tool
def get_current_datetime(format_type: str = "full") -> str:
    """
    Get current date and time in various formats.
    
    Args:
        format_type: 'full', 'date', 'time', 'timestamp'
    
    Examples:
        format_type="full" -> "Monday, January 15, 2024 at 3:45 PM"
        format_type="date" -> "2024-01-15"
        format_type="time" -> "15:45:30"
        format_type="timestamp" -> "1705329930"
    """
    now = datetime.datetime.now()
    
    formats = {
        "full": now.strftime("%A, %B %d, %Y at %I:%M %p"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": str(int(now.timestamp())),
        "iso": now.isoformat()
    }
    
    result = formats.get(format_type.lower(), formats["full"])
    return f"Current {format_type}: {result}"


@tool
def calculate_math(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: Math expression to calculate
    
    Examples:
        "2 + 2"
        "10 * 5 + 3"
        "100 / 4"
        "(5 + 3) * 2"
    """
    try:
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression - only numbers and basic operators allowed"
        
        result = eval(expression, {"__builtins__": {}})
        return f"{expression} = {result}"
    
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating: {e}"


@tool
def timer_countdown(seconds: int, message: str = "Timer complete!") -> str:
    """
    Set a countdown timer (note: returns immediately, timer runs in background).
    
    Args:
        seconds: Duration in seconds
        message: Message to show when complete
    """
    import threading
    import time
    
    def run_timer():
        time.sleep(seconds)
        # In real implementation, this would trigger a notification
        print(f"⏰ TIMER: {message}")
    
    thread = threading.Thread(target=run_timer, daemon=True)
    thread.start()
    
    return f"Timer set for {seconds} seconds ({seconds//60} minutes {seconds%60} seconds)"


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between different units.
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
    
    Supported: inches, feet, meters, kilometers, miles, celsius, fahrenheit, kg, lbs
    """
    conversions = {
        # Length
        ("inches", "feet"): lambda x: x / 12,
        ("feet", "inches"): lambda x: x * 12,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("meters", "feet"): lambda x: x / 0.3048,
        ("kilometers", "miles"): lambda x: x * 0.621371,
        ("miles", "kilometers"): lambda x: x / 0.621371,
        
        # Temperature
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        
        # Weight
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x / 2.20462,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    else:
        return f"Conversion not supported: {from_unit} to {to_unit}"


@tool
def create_json_file(filename: str, data: dict, directory: str = "./data") -> str:
    """
    Create a JSON file with structured data.
    
    Args:
        filename: Name of JSON file
        data: Dictionary to save as JSON
        directory: Where to save the file
    """
    try:
        path = Path(directory) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return f"JSON file created: {path}"
    except Exception as e:
        return f"Error creating JSON file: {e}"


@tool
def read_json_file(filepath: str) -> str:
    """
    Read and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
    """
    try:
        path = Path(filepath)
        
        if not path.exists():
            return f"File not found: {filepath}"
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Pretty print the JSON
        formatted = json.dumps(data, indent=2)
        
        if len(formatted) > 2000:
            return f"JSON content (first 2000 chars):\n{formatted[:2000]}\n... [truncated]"
        
        return f"JSON content:\n{formatted}"
    
    except json.JSONDecodeError:
        return f"Invalid JSON file: {filepath}"
    except Exception as e:
        return f"Error reading JSON: {e}"


@tool
def get_weather(city: str = "auto") -> str:
    """
    Get current weather for a location (requires internet).
    
    Args:
        city: City name or 'auto' for automatic location
    """
    try:
        # Using wttr.in free weather service
        if city == "auto":
            import requests
            response = requests.get("https://wttr.in/?format=3", timeout=5)
        else:
            import requests
            response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        
        if response.status_code == 200:
            return f"🌤️ Weather: {response.text.strip()}"
        else:
            return "Unable to fetch weather data"
    
    except Exception as e:
        return f"Error getting weather: {e}"


@tool
def create_reminder(task: str, time_minutes: int = 60) -> str:
    """
    Create a reminder that will alert after specified time.
    
    Args:
        task: What to remind about
        time_minutes: Minutes until reminder
    """
    import threading
    import time
    
    def remind():
        time.sleep(time_minutes * 60)
        # In production, this would show a system notification
        print(f"⏰ REMINDER: {task}")
    
    thread = threading.Thread(target=remind, daemon=True)
    thread.start()
    
    hours = time_minutes // 60
    mins = time_minutes % 60
    
    time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} minutes"
    
    return f"✅ Reminder set: '{task}' in {time_str}"


@tool  
def generate_password(length: int = 16, include_symbols: bool = True) -> str:
    """
    Generate a random secure password.
    
    Args:
        length: Password length (8-32)
        include_symbols: Include special characters
    """
    import random
    import string
    
    if length < 8 or length > 32:
        return "Password length must be between 8 and 32 characters"
    
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*()_+-=[]{}|"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    
    return f"Generated password ({length} chars): {password}"