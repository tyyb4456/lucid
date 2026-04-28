"""
LUCID Utility Tools — Time, math, conversions, weather, passwords, JSON I/O
"""

from langchain_core.tools import tool
import datetime
import json
from pathlib import Path
from typing import Optional


@tool
def get_current_datetime(format_type: str = "full") -> str:
    """
    Get the current date and/or time in a specified format.

    Use this when the user asks:
    - "What time is it?" / "What's the current time?"    → format_type="time"
    - "What's today's date?"                             → format_type="date"
    - "What day is it?" / "Full date and time"           → format_type="full"
    - "Give me a Unix/epoch timestamp"                   → format_type="timestamp"
    - "ISO format datetime"                              → format_type="iso"

    Args:
        format_type: Output format. One of:
            "full"      → "Monday, January 15, 2024 at 3:45 PM"
            "date"      → "2024-01-15"
            "time"      → "15:45:30"
            "timestamp" → "1705329930"  (Unix epoch, seconds)
            "iso"       → "2024-01-15T15:45:30.123456"
    
    Returns:
        Formatted date/time string.
    """
    now = datetime.datetime.now()

    formats = {
        "full":      now.strftime("%A, %B %d, %Y at %I:%M %p"),
        "date":      now.strftime("%Y-%m-%d"),
        "time":      now.strftime("%H:%M:%S"),
        "timestamp": str(int(now.timestamp())),
        "iso":       now.isoformat(),
    }

    fmt = format_type.lower().strip()
    if fmt not in formats:
        fmt = "full"

    return f"Current {fmt}: {formats[fmt]}"


@tool
def calculate_math(expression: str) -> str:
    """
    Safely evaluate a mathematical expression and return the result.

    Use this for any arithmetic or numeric calculation:
    - Basic arithmetic:  "2 + 2", "100 / 4", "15 * 8"
    - Order of ops:      "(5 + 3) * 2"
    - Percentages:       "340 * 0.15"   (for 15% of 340)
    - Powers:            "2 ** 10"
    - Mixed:             "(100 - 32) * 5 / 9"

    Args:
        expression: A math expression using numbers and operators.
            Allowed operators: + - * / // % ** ( ) .
            NOT supported: variables, functions (sqrt, sin, etc.), text.
            For powers use ** not ^.

    Returns:
        String showing the expression and its result, e.g. "2 ** 10 = 1024".
        Returns a descriptive error message if the expression is invalid.
    """
    import math as _math

    # Whitelist: digits, operators, parens, whitespace, decimal point
    allowed_chars = set("0123456789+-*/.%() ")
    # Also allow ** for powers (two chars but both in allowed set already)
    if not all(c in allowed_chars for c in expression):
        return (
            f"Invalid expression: '{expression}'. "
            "Only numbers and operators (+, -, *, /, //, %, **, parentheses) are allowed."
        )

    try:
        result = eval(expression, {"__builtins__": {}}, {})

        # Format: avoid ugly floating point noise for clean integers
        if isinstance(result, float) and result.is_integer():
            formatted = str(int(result))
        elif isinstance(result, float):
            formatted = f"{result:.6g}"  # up to 6 significant figures, no trailing zeros
        else:
            formatted = str(result)

        return f"{expression} = {formatted}"

    except ZeroDivisionError:
        return "Error: Division by zero."
    except SyntaxError:
        return f"Error: '{expression}' is not a valid math expression."
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def timer_countdown(seconds: int, message: str = "Timer complete!") -> str:
    """
    Start a background countdown timer that prints an alert when it expires.

    Use this when the user asks to:
    - "Set a timer for X seconds/minutes/hours"
    - "Alert me in X minutes"
    - "Countdown for X seconds"

    Note: Convert user input to seconds before calling.
    Examples: 5 minutes → 300, 1 hour → 3600, 90 seconds → 90

    Args:
        seconds: Duration of the timer in seconds. Must be a positive integer.
        message: Message to display when the timer fires. 
                 Default: "Timer complete!"
                 Customize with context: "Time to take a break!", "Meeting starting!"

    Returns:
        Confirmation string showing duration in human-readable format.
    """
    import threading
    import time

    if seconds <= 0:
        return "Error: Timer duration must be greater than 0 seconds."
    if seconds > 86400:
        return "Error: Timer duration cannot exceed 24 hours (86400 seconds)."

    def run_timer():
        time.sleep(seconds)
        print(f"\n⏰ TIMER ALERT: {message}\n")

    thread = threading.Thread(target=run_timer, daemon=True)
    thread.start()

    # Human-readable duration
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")
    duration_str = " ".join(parts)

    return f"✅ Timer set: {duration_str} — will alert: \"{message}\""


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert a numeric value between supported units of measurement.

    Use this when the user asks:
    - "Convert X miles to kilometers"
    - "How many feet is 2 meters?"
    - "72°F in Celsius"
    - "How many lbs is 85 kg?"
    - "Convert 12 inches to feet"

    Args:
        value: The numeric value to convert (e.g., 5.0, 72, 100).
        from_unit: Source unit (see supported list below).
        to_unit: Target unit (see supported list below).

    Supported unit pairs:
        LENGTH:      inches ↔ feet, feet ↔ meters, meters ↔ kilometers,
                     kilometers ↔ miles, miles ↔ feet, inches ↔ meters
        TEMPERATURE: celsius ↔ fahrenheit, celsius ↔ kelvin, fahrenheit ↔ kelvin
        WEIGHT:      kg ↔ lbs, kg ↔ grams, lbs ↔ ounces
        TIME:        seconds ↔ minutes, minutes ↔ hours, hours ↔ days

    Returns:
        Formatted conversion result, e.g. "5.0 miles = 8.05 kilometers".
        Returns an error message listing supported conversions if pair is unsupported.
    """
    conversions = {
        # Length
        ("inches", "feet"):        lambda x: x / 12,
        ("feet", "inches"):        lambda x: x * 12,
        ("feet", "meters"):        lambda x: x * 0.3048,
        ("meters", "feet"):        lambda x: x / 0.3048,
        ("meters", "kilometers"):  lambda x: x / 1000,
        ("kilometers", "meters"):  lambda x: x * 1000,
        ("kilometers", "miles"):   lambda x: x * 0.621371,
        ("miles", "kilometers"):   lambda x: x / 0.621371,
        ("miles", "feet"):         lambda x: x * 5280,
        ("feet", "miles"):         lambda x: x / 5280,
        ("inches", "meters"):      lambda x: x * 0.0254,
        ("meters", "inches"):      lambda x: x / 0.0254,

        # Temperature
        ("celsius", "fahrenheit"):  lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"):  lambda x: (x - 32) * 5 / 9,
        ("celsius", "kelvin"):      lambda x: x + 273.15,
        ("kelvin", "celsius"):      lambda x: x - 273.15,
        ("fahrenheit", "kelvin"):   lambda x: (x - 32) * 5 / 9 + 273.15,
        ("kelvin", "fahrenheit"):   lambda x: (x - 273.15) * 9 / 5 + 32,

        # Weight
        ("kg", "lbs"):              lambda x: x * 2.20462,
        ("lbs", "kg"):              lambda x: x / 2.20462,
        ("kg", "grams"):            lambda x: x * 1000,
        ("grams", "kg"):            lambda x: x / 1000,
        ("lbs", "ounces"):          lambda x: x * 16,
        ("ounces", "lbs"):          lambda x: x / 16,

        # Time
        ("seconds", "minutes"):     lambda x: x / 60,
        ("minutes", "seconds"):     lambda x: x * 60,
        ("minutes", "hours"):       lambda x: x / 60,
        ("hours", "minutes"):       lambda x: x * 60,
        ("hours", "days"):          lambda x: x / 24,
        ("days", "hours"):          lambda x: x * 24,
    }

    key = (from_unit.lower().strip(), to_unit.lower().strip())

    if key not in conversions:
        # Check if the units exist but in wrong direction
        reverse = (key[1], key[0])
        if reverse in conversions:
            return (
                f"Conversion from '{from_unit}' to '{to_unit}' is not defined, "
                f"but '{to_unit}' to '{from_unit}' is. Did you mean to reverse them?"
            )
        return (
            f"Unsupported conversion: '{from_unit}' → '{to_unit}'. "
            "Supported categories: length, temperature, weight, time. "
            "Check spelling (e.g. 'celsius', 'fahrenheit', 'kg', 'lbs', 'miles', 'kilometers')."
        )

    result = conversions[key](value)

    # Clean formatting
    if isinstance(result, float):
        formatted = f"{result:.4g}" if abs(result) >= 0.001 else f"{result:.6e}"
    else:
        formatted = str(result)

    return f"{value} {from_unit} = {formatted} {to_unit}"


@tool
def create_json_file(filename: str, data: dict, directory: str = "./data") -> str:
    """
    Serialize a Python dictionary to a formatted JSON file on disk.

    Use this when the user wants to:
    - "Save this data as JSON"
    - "Create a config/settings/output JSON file"
    - "Store these results in a JSON file"

    Args:
        filename: Name of the JSON file, e.g. "config.json", "output.json".
                  Will be created or overwritten if it already exists.
        data: Python dictionary to serialize. Must be JSON-serializable
              (strings, numbers, lists, dicts, booleans, None).
        directory: Directory path where the file will be saved.
                   Default is "./data". Created automatically if it doesn't exist.

    Returns:
        Success message with full file path, or error description.
    """
    try:
        # Ensure filename ends with .json
        if not filename.endswith(".json"):
            filename += ".json"

        path = Path(directory) / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size = path.stat().st_size
        return f"✅ JSON file saved: {path.resolve()}  ({size} bytes)"

    except TypeError as e:
        return f"Error: Data is not JSON-serializable — {e}"
    except PermissionError:
        return f"Error: Permission denied writing to '{directory}'."
    except Exception as e:
        return f"Error creating JSON file: {e}"


@tool
def read_json_file(filepath: str) -> str:
    """
    Read and display the contents of a JSON file.

    Use this when the user wants to:
    - "Read / show / print the contents of X.json"
    - "What's in config.json?"
    - "Load data from output.json"

    Args:
        filepath: Full or relative path to the JSON file.
                  Examples: "./data/config.json", "C:/Users/user/output.json"

    Returns:
        Pretty-printed JSON content (up to 3000 characters), or an error message.
        Large files are truncated with a notice.
    """
    try:
        path = Path(filepath)

        if not path.exists():
            return f"File not found: '{filepath}'. Check the path and try again."

        if path.suffix.lower() != ".json":
            return f"Warning: '{filepath}' does not have a .json extension. Attempting to read anyway."

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        char_limit = 3000

        if len(formatted) > char_limit:
            return (
                f"JSON content (truncated — showing first {char_limit} of {len(formatted)} chars):\n"
                f"{formatted[:char_limit]}\n... [truncated — full file at {path.resolve()}]"
            )

        return f"JSON content from '{path.name}':\n{formatted}"

    except json.JSONDecodeError as e:
        return f"Invalid JSON in '{filepath}': {e}"
    except PermissionError:
        return f"Error: Permission denied reading '{filepath}'."
    except Exception as e:
        return f"Error reading JSON file: {e}"


@tool
def get_weather(city: str = "auto") -> str:
    """
    Fetch the current weather conditions for a city.

    Use this when the user asks:
    - "What's the weather?" / "How's the weather outside?"  → city="auto"
    - "Weather in Lahore"                                   → city="Lahore"
    - "Is it raining in London?"                            → city="London"
    - "Temperature in New York right now"                   → city="New York"

    Args:
        city: City name to look up.
              Use "auto" to detect the user's current location automatically.
              For multi-word cities use the full name: "New York", "Los Angeles", "Kuala Lumpur".

    Returns:
        Current weather conditions string (temperature, condition, location),
        or an error if the service is unreachable.

    Note: Requires internet access. Uses the wttr.in public weather service.
    """
    try:
        import requests

        if city.lower() == "auto":
            url = "https://wttr.in/?format=3"
        else:
            # URL-encode city name for multi-word cities
            encoded = city.strip().replace(" ", "+")
            url = f"https://wttr.in/{encoded}?format=3"

        response = requests.get(url, timeout=6)
        response.raise_for_status()

        weather_text = response.text.strip()
        if not weather_text:
            return "No weather data returned. The city name may be unrecognized."

        return f"🌤️ {weather_text}"

    except requests.exceptions.Timeout:
        return "Error: Weather service timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return "Error: Unable to reach weather service. Check your internet connection."
    except Exception as e:
        return f"Error fetching weather: {e}"


@tool
def create_reminder(task: str, time_minutes: int = 60) -> str:
    """
    Schedule a background reminder that fires after a specified number of minutes.

    Use this when the user asks to:
    - "Remind me to [task] in X minutes/hours"
    - "Set a reminder for [task] in 30 minutes"
    - "Alert me to [task] in 2 hours" → time_minutes=120

    Note: Convert user input to minutes before calling.
    Examples: 2 hours → 120, 1.5 hours → 90, 30 minutes → 30.

    Args:
        task: The reminder message, e.g. "Call Ahmed", "Take medication", "Submit report".
              Keep it concise and action-oriented.
        time_minutes: How many minutes until the reminder fires. Must be positive.
                      Default: 60 minutes.

    Returns:
        Confirmation with the task and when it will fire, or an error message.
    """
    import threading
    import time

    if time_minutes <= 0:
        return "Error: Reminder time must be greater than 0 minutes."
    if time_minutes > 1440:
        return "Error: Reminder time cannot exceed 24 hours (1440 minutes)."
    if not task.strip():
        return "Error: Reminder task cannot be empty."

    def remind():
        time.sleep(time_minutes * 60)
        print(f"\n⏰ REMINDER: {task}\n")

    thread = threading.Thread(target=remind, daemon=True)
    thread.start()

    # Human-readable time
    hours = time_minutes // 60
    mins = time_minutes % 60
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if mins:
        parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
    time_str = " and ".join(parts)

    return f"✅ Reminder set: \"{task}\" — fires in {time_str}"


@tool
def generate_password(length: int = 16, include_symbols: bool = True) -> str:
    """
    Generate a cryptographically random secure password.

    Use this when the user asks to:
    - "Generate a password" / "Create a strong password"
    - "Give me a 20-character password with symbols"
    - "Make a simple password without special characters"

    Args:
        length: Length of the password in characters.
                Allowed range: 8–64. Default: 16.
                Use shorter (8–12) for simple/memorable, longer (20+) for high security.
        include_symbols: Whether to include special characters (!@#$%^&*...).
                         True (default): maximum security.
                         False: alphanumeric only (letters + digits), easier to type.

    Returns:
        The generated password with a brief strength label.
    """
    import secrets
    import string

    if not (8 <= length <= 64):
        return f"Error: Password length must be between 8 and 64 characters (requested: {length})."

    chars = string.ascii_letters + string.digits
    symbol_set = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if include_symbols:
        chars += symbol_set

    # Use secrets for cryptographic randomness (better than random)
    # Guarantee at least one of each required character class
    password_chars = []
    password_chars.append(secrets.choice(string.ascii_uppercase))
    password_chars.append(secrets.choice(string.ascii_lowercase))
    password_chars.append(secrets.choice(string.digits))
    if include_symbols:
        password_chars.append(secrets.choice(symbol_set))

    # Fill the rest randomly
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(chars))

    # Shuffle to avoid predictable positions
    secrets.SystemRandom().shuffle(password_chars)
    password = "".join(password_chars)

    symbol_label = "with symbols" if include_symbols else "alphanumeric only"
    strength = "Strong" if length >= 16 and include_symbols else "Moderate" if length >= 12 else "Basic"

    return f"🔐 Password ({length} chars, {symbol_label}, {strength}): {password}"