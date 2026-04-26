"""
LUCID Automation Tools - Mouse, Keyboard, Screenshot, Clipboard
Capabilities: Full GUI automation, screen capture, clipboard management
"""

from langchain_core.tools import tool
import pyautogui
import datetime
from pathlib import Path
from typing import Optional

# Set PyAutoGUI safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Pause between actions

@tool
def click_mouse(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """
    Click the mouse at specific screen coordinates.
    
    Args:
        x: X coordinate on screen
        y: Y coordinate on screen
        button: 'left', 'right', or 'middle'
        clicks: Number of clicks (1=single, 2=double)
    
    Examples:
        x=500, y=300, button="left"
        x=100, y=100, clicks=2  (double-click)
    """
    try:
        screen_width, screen_height = pyautogui.size()
        
        if x < 0 or x > screen_width or y < 0 or y > screen_height:
            return f"Coordinates out of range. Screen size: {screen_width}x{screen_height}"
        
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        return f"Clicked {button} button at ({x}, {y})"
    
    except Exception as e:
        return f"Error clicking mouse: {e}"


@tool
def move_mouse(x: int, y: int, duration: float = 0.5) -> str:
    """
    Move mouse to specific coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        duration: Time to take (seconds) - 0 for instant
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})"
    except Exception as e:
        return f"Error moving mouse: {e}"


@tool
def get_mouse_position() -> str:
    """Get current mouse cursor position."""
    try:
        x, y = pyautogui.position()
        return f"Mouse position: ({x}, {y})"
    except Exception as e:
        return f"Error getting mouse position: {e}"


@tool
def type_text(text: str, interval: float = 0.05) -> str:
    """
    Type text as if typing on keyboard.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes (seconds)
    
    Examples:
        "Hello, World!"
        "This is automated typing"
    """
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: '{text[:50]}...'" if len(text) > 50 else f"Typed: '{text}'"
    except Exception as e:
        return f"Error typing text: {e}"


@tool
def press_key(key: str, presses: int = 1) -> str:
    """
    Press a keyboard key or key combination.
    
    Args:
        key: Key name or combination
        presses: Number of times to press
    
    Examples:
        "enter"
        "ctrl+c" (copy)
        "ctrl+v" (paste)
        "alt+tab" (switch window)
        "win+r" (run dialog)
    
    Available keys: enter, esc, tab, space, backspace, delete,
                    up, down, left, right, home, end, pageup, pagedown,
                    f1-f12, ctrl, alt, shift, win
    """
    try:
        # Handle key combinations (ctrl+c, alt+tab, etc.)
        if '+' in key:
            keys = key.split('+')
            pyautogui.hotkey(*keys)
            return f"Pressed key combination: {key}"
        else:
            pyautogui.press(key, presses=presses)
            return f"Pressed key: {key} ({presses} time(s))"
    
    except Exception as e:
        return f"Error pressing key: {e}"


@tool
def take_screenshot(save_name: str = "", region: Optional[tuple] = None) -> str:
    """
    Take a screenshot of the entire screen or a specific region.
    
    Args:
        save_name: Custom filename (optional)
        region: Tuple of (x, y, width, height) for partial screenshot
    
    Examples:
        save_name="my_screen.png"
        region=(0, 0, 800, 600)  (top-left 800x600 pixels)
    """
    try:
        screenshots_dir = Path("./data/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = save_name if save_name else f"screenshot_{timestamp}.png"
        filepath = screenshots_dir / filename
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(filepath)
        return f"Screenshot saved: {filepath}"
    
    except Exception as e:
        return f"Screenshot failed: {e}"


@tool
def find_on_screen(image_path: str, confidence: float = 0.8) -> str:
    """
    Find an image on the screen and return its position.
    
    Args:
        image_path: Path to image file to find
        confidence: Match confidence (0-1)
    
    Returns coordinates if found, or error if not found.
    """
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location:
            x, y = pyautogui.center(location)
            return f"Found image at ({x}, {y})"
        else:
            return f"Image not found on screen: {image_path}"
    
    except Exception as e:
        return f"Error finding image: {e}"


@tool
def scroll(clicks: int, direction: str = "down") -> str:
    """
    Scroll the mouse wheel.
    
    Args:
        clicks: Number of scroll clicks
        direction: 'up' or 'down'
    """
    try:
        amount = clicks if direction == "up" else -clicks
        pyautogui.scroll(amount)
        return f"Scrolled {direction} {clicks} clicks"
    except Exception as e:
        return f"Error scrolling: {e}"


@tool
def get_screen_size() -> str:
    """Get the screen resolution."""
    try:
        width, height = pyautogui.size()
        return f"Screen resolution: {width}x{height}"
    except Exception as e:
        return f"Error getting screen size: {e}"


@tool
def read_clipboard() -> str:
    """Read the current clipboard content."""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            if len(data) > 1000:
                return f"Clipboard content (first 1000 chars):\n{data[:1000]}\n... [truncated]"
            return f"Clipboard content:\n{data}"
        except:
            win32clipboard.CloseClipboard()
            return "Clipboard is empty or contains non-text data"
    
    except Exception as e:
        return f"Error reading clipboard: {e}"


@tool
def write_clipboard(text: str) -> str:
    """
    Write text to the clipboard.
    
    Args:
        text: Text to copy to clipboard
    """
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        
        return f"Copied to clipboard: '{text[:100]}...'" if len(text) > 100 else f"Copied to clipboard: '{text}'"
    
    except Exception as e:
        return f"Error writing to clipboard: {e}"


@tool
def alert_box(message: str, title: str = "LUCID Alert") -> str:
    """
    Display a system alert/message box.
    
    Args:
        message: Message to display
        title: Alert window title
    """
    try:
        pyautogui.alert(text=message, title=title)
        return f"Displayed alert: {title}"
    except Exception as e:
        return f"Error displaying alert: {e}"