"""
LUCID — Automation Tools
Capabilities: GUI automation · mouse & keyboard · screen capture · clipboard
Platform: Windows (pyautogui + win32clipboard)
"""

from langchain_core.tools import tool
import pyautogui
import datetime
from pathlib import Path
from typing import Optional

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True   # Move mouse to any corner to abort
pyautogui.PAUSE = 0.4       # Brief pause between actions for stability


# ─────────────────────────────────────────────
# MOUSE TOOLS
# ─────────────────────────────────────────────

@tool
def click_mouse(
    x: int,
    y: int,
    button: str = "left",
    clicks: int = 1,
    interval: float = 0.1
) -> str:
    """
    Click the mouse at specific screen coordinates.

    Use this to press buttons, select items, check checkboxes, or interact
    with any clickable UI element. For opening files or apps, use clicks=2
    (double-click). For context menus, use button="right".

    Args:
        x:        Horizontal screen coordinate (pixels from left edge).
        y:        Vertical screen coordinate (pixels from top edge).
        button:   Which mouse button — "left" (default), "right", or "middle".
        clicks:   How many times to click — 1 for single-click, 2 for double-click.
        interval: Seconds between consecutive clicks when clicks > 1.

    Returns:
        Confirmation string with the action taken, or an error message.

    When to use:
        - Clicking a button or menu item           → button="left", clicks=1
        - Opening a file or launching an app icon  → button="left", clicks=2
        - Opening a right-click context menu       → button="right", clicks=1

    Safety note:
        Always call get_screen_size() first if unsure of coordinate bounds.
        Coordinates outside the screen are rejected with an error.
    """
    try:
        screen_w, screen_h = pyautogui.size()
        if not (0 <= x <= screen_w) or not (0 <= y <= screen_h):
            return (
                f"ERROR: Coordinates ({x}, {y}) are outside the screen "
                f"({screen_w}x{screen_h}). Call get_screen_size() and recalculate."
            )
        if button not in ("left", "right", "middle"):
            return f"ERROR: Invalid button '{button}'. Must be 'left', 'right', or 'middle'."
        if clicks not in (1, 2, 3):
            return f"ERROR: clicks must be 1, 2, or 3. Got {clicks}."

        pyautogui.click(x=x, y=y, clicks=clicks, button=button, interval=interval)
        action = "Double-clicked" if clicks == 2 else "Clicked"
        return f"{action} {button} button at ({x}, {y})."
    except Exception as e:
        return f"ERROR clicking mouse: {e}"


@tool
def move_mouse(x: int, y: int, duration: float = 0.3) -> str:
    """
    Move the mouse cursor to specific coordinates WITHOUT clicking.

    Use this to hover over an element to reveal a tooltip or dropdown,
    or to visually verify target position before a subsequent click_mouse call.

    Args:
        x:        Horizontal screen coordinate.
        y:        Vertical screen coordinate.
        duration: Time in seconds to animate the movement (0 = instant).
                  Use 0.3–0.8 for human-like movement; 0 for speed.

    Returns:
        Confirmation of final mouse position, or an error message.
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        actual_x, actual_y = pyautogui.position()
        return f"Mouse moved to ({actual_x}, {actual_y})."
    except Exception as e:
        return f"ERROR moving mouse: {e}"


@tool
def get_mouse_position() -> str:
    """
    Return the current (x, y) position of the mouse cursor.

    Use this to discover coordinates of a point the user is hovering over,
    or to debug unexpected cursor positions mid-automation.

    Returns:
        String with current mouse coordinates.
    """
    try:
        x, y = pyautogui.position()
        return f"Mouse is currently at ({x}, {y})."
    except Exception as e:
        return f"ERROR getting mouse position: {e}"


@tool
def drag_mouse(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    button: str = "left",
    duration: float = 0.5
) -> str:
    """
    Click and drag from one position to another (drag-and-drop).

    Use this to move files/items in a UI, resize windows by dragging edges,
    draw in paint-like apps, or drag sliders.

    Args:
        start_x:  X coordinate to start the drag (mouse-down position).
        start_y:  Y coordinate to start the drag.
        end_x:    X coordinate where the drag ends (mouse-up position).
        end_y:    Y coordinate where the drag ends.
        button:   Mouse button to hold during drag — "left" (default) or "right".
        duration: Seconds to animate the drag motion (0.3–1.0 recommended).

    Returns:
        Confirmation of the drag path, or an error message.

    When to use:
        - Move a file icon from one folder to another
        - Resize a window by dragging its edge
        - Reorder items in a list by drag-and-drop
        - Adjust a slider control
    """
    try:
        screen_w, screen_h = pyautogui.size()
        for name, cx, cy in [("start", start_x, start_y), ("end", end_x, end_y)]:
            if not (0 <= cx <= screen_w) or not (0 <= cy <= screen_h):
                return (
                    f"ERROR: {name} coordinates ({cx}, {cy}) are outside "
                    f"the screen ({screen_w}x{screen_h})."
                )
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) using {button} button."
    except Exception as e:
        return f"ERROR during drag: {e}"


@tool
def scroll(clicks: int, direction: str = "down", x: Optional[int] = None, y: Optional[int] = None) -> str:
    """
    Scroll the mouse wheel at the current or specified position.

    Use this to scroll web pages, document editors, file explorers, or
    any scrollable panel. Scroll to expose content that is off-screen.

    Args:
        clicks:    Number of scroll steps. Use 3–5 for small nudges,
                   10–20 for larger jumps.
        direction: "down" (default) to scroll toward the bottom,
                   "up" to scroll toward the top.
        x:         Optional X coordinate to scroll at. Defaults to current position.
        y:         Optional Y coordinate to scroll at. Defaults to current position.

    Returns:
        Confirmation of the scroll action, or an error message.
    """
    try:
        if direction not in ("up", "down"):
            return f"ERROR: direction must be 'up' or 'down'. Got '{direction}'."
        amount = clicks if direction == "up" else -clicks
        if x is not None and y is not None:
            pyautogui.scroll(amount, x=x, y=y)
            return f"Scrolled {direction} {clicks} steps at ({x}, {y})."
        else:
            pyautogui.scroll(amount)
            return f"Scrolled {direction} {clicks} steps at current cursor position."
    except Exception as e:
        return f"ERROR scrolling: {e}"


# ─────────────────────────────────────────────
# KEYBOARD TOOLS
# ─────────────────────────────────────────────

@tool
def type_text(text: str, interval: float = 0.04) -> str:
    """
    Type a string of text into the currently focused input field or app.

    Use this for filling in text fields, search boxes, document editors,
    terminal input, or any text entry area. The target field must already
    be focused (clicked) before calling this tool.

    Args:
        text:     The exact text to type. Supports letters, numbers,
                  punctuation, and spaces. Does NOT support special keys
                  like Enter or Tab — use press_key() for those.
        interval: Seconds between each keystroke (default 0.04).
                  Increase to 0.08–0.15 for slower, more reliable typing
                  in apps that drop keystrokes.

    Returns:
        Confirmation of the text typed (truncated if > 80 chars), or an error.

    When to use:
        - Fill a form field: click the field first, then type_text(value)
        - Type a filename in a Save dialog
        - Enter a search query in a browser or app

    Limitations:
        - Only printable ASCII characters work reliably with pyautogui.write().
        - For unicode/emoji or very long text (>500 chars), prefer
          write_clipboard() + press_key("ctrl+v") for better reliability.
    """
    try:
        if not text:
            return "ERROR: text cannot be empty."
        pyautogui.write(text, interval=interval)
        display = f"'{text[:80]}…'" if len(text) > 80 else f"'{text}'"
        return f"Typed {display} ({len(text)} character{'s' if len(text) != 1 else ''})."
    except Exception as e:
        return f"ERROR typing text: {e}"


@tool
def press_key(key: str, presses: int = 1, interval: float = 0.1) -> str:
    """
    Press a keyboard key or key combination (shortcut).

    Use this for navigation keys, function keys, and keyboard shortcuts.
    For combinations, join keys with '+' (e.g., "ctrl+c", "alt+f4").

    Args:
        key:      Key name or combination. See examples below.
        presses:  How many times to press the key (default 1).
        interval: Seconds between repeated presses when presses > 1.

    Returns:
        Confirmation of the key pressed, or an error message.

    Common single keys:
        "enter", "esc", "tab", "space", "backspace", "delete"
        "up", "down", "left", "right"
        "home", "end", "pageup", "pagedown"
        "f1" … "f12"
        "printscreen", "insert", "numlock", "capslock"

    Common shortcuts (use '+' to combine):
        "ctrl+c"          → Copy
        "ctrl+v"          → Paste
        "ctrl+x"          → Cut
        "ctrl+z"          → Undo
        "ctrl+s"          → Save
        "ctrl+a"          → Select all
        "ctrl+w"          → Close tab/window
        "ctrl+t"          → New browser tab
        "ctrl+shift+t"    → Reopen closed tab
        "alt+tab"         → Switch window
        "alt+f4"          → Close active window
        "win+d"           → Show desktop
        "win+r"           → Open Run dialog
        "win+l"           → Lock screen
        "ctrl+alt+delete" → Task manager / lock screen
        "ctrl+shift+esc"  → Open Task Manager directly
    """
    try:
        if not key:
            return "ERROR: key cannot be empty."
        if presses < 1:
            return f"ERROR: presses must be at least 1. Got {presses}."

        if "+" in key:
            parts = key.lower().split("+")
            pyautogui.hotkey(*parts)
            return f"Pressed shortcut: {key}."
        else:
            pyautogui.press(key.lower(), presses=presses, interval=interval)
            times = f"{presses} time{'s' if presses > 1 else ''}"
            return f"Pressed key '{key}' {times}."
    except Exception as e:
        return f"ERROR pressing key '{key}': {e}"


# ─────────────────────────────────────────────
# SCREEN TOOLS
# ─────────────────────────────────────────────

@tool
def take_screenshot(
    save_name: str = "",
    region: Optional[tuple] = None
) -> str:
    """
    Capture the screen and save it as a PNG file.

    Use this to observe the current UI state before acting, verify that
    an action succeeded, or capture a specific region of the screen.
    Screenshots are saved to ./data/screenshots/.

    Args:
        save_name: Custom filename (e.g., "before_login.png").
                   If empty, a timestamped name is auto-generated.
        region:    Optional (x, y, width, height) tuple to capture only
                   part of the screen. Example: (0, 0, 800, 600) captures
                   the top-left 800×600 pixels. Omit for full screen.

    Returns:
        The full file path of the saved screenshot, or an error message.

    Best practices:
        - Take a screenshot at the START of an ambiguous task to see
          the current state before deciding what to do.
        - Take a screenshot AFTER major actions (submit, navigate, type)
          to verify the result.
        - Use descriptive names: "after_form_submit.png", "error_dialog.png"
        - Use region to focus on a specific area and reduce noise.
    """
    try:
        screenshots_dir = Path("./data/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = save_name if save_name else f"screenshot_{timestamp}.png"
        if not filename.endswith(".png"):
            filename += ".png"
        filepath = screenshots_dir / filename

        screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        screenshot.save(filepath)

        region_str = f" (region {region})" if region else " (full screen)"
        return f"Screenshot saved{region_str}: {filepath}"
    except Exception as e:
        return f"ERROR taking screenshot: {e}"


@tool
def find_on_screen(image_path: str, confidence: float = 0.8) -> str:
    """
    Locate a reference image on the screen and return its center coordinates.

    Use this when you don't know the exact pixel coordinates of a UI element,
    but you have (or can infer) a small screenshot of what it looks like.
    This is more robust than hardcoding coordinates.

    Args:
        image_path:  Path to a PNG/BMP reference image of the element to find.
                     The image should be cropped as tightly as possible around
                     the target element.
        confidence:  Match threshold from 0.0 to 1.0 (default 0.8).
                     Lower values (e.g., 0.6) are more lenient and tolerate
                     slight scaling or rendering differences.
                     Higher values (e.g., 0.95) require a near-exact match.

    Returns:
        "(x, y)" of the element's center if found, or a not-found message.

    When to use:
        - Clicking a specific button whose position may vary
        - Verifying a UI element is visible ("Is the Save button on screen?")
        - Locating icons, logos, or recurring UI patterns

    On failure:
        If not found, lower confidence to 0.6 and retry once.
        If still not found, call take_screenshot() and ask the user
        to confirm whether the element is currently visible.
    """
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            cx, cy = pyautogui.center(location)
            return (
                f"Found at center ({cx}, {cy}). "
                f"Bounding box: x={location.left}, y={location.top}, "
                f"w={location.width}, h={location.height}."
            )
        return (
            f"Image not found on screen: '{image_path}' "
            f"(confidence={confidence}). "
            "Try lowering confidence to 0.6, or take a screenshot to verify UI state."
        )
    except FileNotFoundError:
        return f"ERROR: Reference image file not found: '{image_path}'."
    except Exception as e:
        return f"ERROR finding image on screen: {e}"


@tool
def get_screen_size() -> str:
    """
    Return the screen resolution (width × height) in pixels.

    Call this first whenever you need to calculate relative positions,
    check if coordinates are in bounds, or center an element on screen.

    Returns:
        Screen dimensions as a string, e.g., "Screen resolution: 1920x1080".
    """
    try:
        w, h = pyautogui.size()
        center_x, center_y = w // 2, h // 2
        return (
            f"Screen resolution: {w}x{h} pixels. "
            f"Center point: ({center_x}, {center_y}). "
            f"Valid coordinate range: x=0–{w}, y=0–{h}."
        )
    except Exception as e:
        return f"ERROR getting screen size: {e}"


# ─────────────────────────────────────────────
# CLIPBOARD TOOLS
# ─────────────────────────────────────────────

@tool
def read_clipboard() -> str:
    """
    Read and return the current text content of the Windows clipboard.

    Use this to:
    - Verify clipboard content before pasting into a critical field
    - Capture text that the user or a previous automation step copied
    - Check what was last copied from a webpage or document

    Returns:
        The clipboard text (truncated to 2000 chars if very long),
        or a message if the clipboard is empty or contains non-text data.

    Note:
        This tool only reads plain text. Images, files, and rich-text
        clipboard content will return an empty or error result.
    """
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            if not data:
                return "Clipboard is empty."
            if len(data) > 2000:
                return (
                    f"Clipboard content ({len(data)} chars, showing first 2000):\n"
                    f"{data[:2000]}\n[… truncated]"
                )
            return f"Clipboard content ({len(data)} chars):\n{data}"
        except TypeError:
            win32clipboard.CloseClipboard()
            return "Clipboard contains non-text data (e.g., an image or file)."
    except Exception as e:
        return f"ERROR reading clipboard: {e}"


@tool
def write_clipboard(text: str) -> str:
    """
    Write text to the Windows clipboard so it can be pasted anywhere.

    Prefer this over type_text() for:
    - Long strings (>100 characters) — faster and more reliable
    - Text with special or unicode characters that type_text() may mangle
    - Preserving exact formatting (code, paths, URLs)

    After calling this, use press_key("ctrl+v") to paste into the target field.

    Args:
        text: The plain text to copy to the clipboard.
              Overwrites any existing clipboard content.

    Returns:
        Confirmation with a preview of the text copied, or an error message.

    Workflow:
        1. write_clipboard(text)           → copies text
        2. click_mouse(field_x, field_y)   → focus the input field
        3. press_key("ctrl+v")             → pastes text into field
    """
    try:
        if not text:
            return "ERROR: Cannot write empty text to clipboard."
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()

        preview = f"'{text[:100]}…'" if len(text) > 100 else f"'{text}'"
        return f"Copied {len(text)} chars to clipboard: {preview}."
    except Exception as e:
        return f"ERROR writing to clipboard: {e}"


# ─────────────────────────────────────────────
# UTILITY TOOLS
# ─────────────────────────────────────────────

@tool
def alert_box(message: str, title: str = "LUCID") -> str:
    """
    Show a blocking system alert dialog with a message.

    Use this to notify the user of something that requires their attention
    before the automation continues — for example, confirming a dangerous
    action was completed, or asking them to manually handle an unexpected
    dialog. The user must click OK to dismiss the alert.

    Args:
        message: The message text to display in the alert body.
        title:   Window title shown at the top of the dialog.

    Returns:
        Confirmation that the dialog was shown and dismissed, or an error.

    Use sparingly — prefer returning a message to the main agent instead
    of showing an alert, unless the user must physically interact with
    the dialog before automation can continue.
    """
    try:
        pyautogui.alert(text=message, title=title, button="OK")
        return f"Alert dismissed by user. Title: '{title}' | Message: '{message[:100]}'."
    except Exception as e:
        return f"ERROR displaying alert: {e}"