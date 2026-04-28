"""
LUCID System Control Tools — Full Windows PC Control
Capabilities: Process management, power control, window management, system info
"""

from langchain_core.tools import tool
import subprocess
import psutil
import os
from pathlib import Path


# ─────────────────────────────────────────────
# TOOL 1 — Execute Command (Last Resort)
# ─────────────────────────────────────────────

@tool
def execute_command(command: str, shell: str = "powershell") -> str:
    """
    Execute a raw system command via PowerShell, CMD, or Bash.

    ⚠️ USE AS LAST RESORT ONLY.
    Prefer dedicated tools for common tasks:
      - Opening apps       → open_any_application
      - Killing processes  → kill_process
      - Listing processes  → list_running_processes
      - System stats       → get_system_info
      - Window control     → manage_window
      - Power actions      → system_power_control

    Use execute_command ONLY when no dedicated tool covers the task.
    Examples of valid uses:
      - Setting environment variables
      - Querying registry keys
      - Running scripts (.ps1, .bat, .sh)
      - Network diagnostics (ipconfig, netstat, ping)
      - Installing packages (winget, pip, npm)
      - Any advanced OS operation not covered by other tools

    Args:
        command: The command string to execute.
        shell: 'powershell' (default), 'cmd', or 'bash'.

    Returns:
        stdout output, or stderr if stdout is empty. Capped at 3000 characters.
    """
    try:
        if shell == "powershell":
            result = subprocess.run(
                ["powershell", "-NonInteractive", "-Command", command],
                capture_output=True, text=True, timeout=30
            )
        else:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

        output = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
        if not output:
            return "Command executed successfully (no output returned)."
        return f"Output:\n{output[:3000]}"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {e}"


# ─────────────────────────────────────────────
# TOOL 2 — Open Application
# ─────────────────────────────────────────────

@tool
def open_any_application(app_path_or_name: str, arguments: str = "") -> str:
    """
    Launch an application, open a file with its default program, or open a URL.

    Use this tool when the user wants to:
      - Open/launch/start any program (by name or full path)
      - Open a file (e.g., a .pdf, .docx) with its default app
      - Open a website URL in the default browser

    Resolves apps in this order:
      1. URL → opens in default browser
      2. Exact file/exe path → launches directly
      3. App name → searches system PATH via PowerShell
      4. Fallback → attempts shell execution

    Args:
        app_path_or_name:
            - App name:    "notepad", "discord", "code", "chrome"
            - Full path:   "C:\\Program Files\\Spotify\\Spotify.exe"
            - File path:   "C:\\Users\\tayyab\\report.pdf"
            - URL:         "https://youtube.com"
        arguments: Optional CLI arguments to pass to the app.

    Returns:
        Confirmation of what was launched, or an error message.
    """
    try:
        # Case 1: URL
        if app_path_or_name.startswith(("http://", "https://")):
            import webbrowser
            webbrowser.open(app_path_or_name)
            return f"Opened URL in default browser: {app_path_or_name}"

        # Case 2: Exact path exists
        resolved = Path(app_path_or_name)
        if resolved.exists():
            cmd = f'Start-Process "{resolved}" {("-ArgumentList " + arguments) if arguments else ""}'
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            return f"Launched: {resolved}"

        # Case 3: Search by name in system PATH
        search_cmd = (
            f'Get-Command "{app_path_or_name}*" -ErrorAction SilentlyContinue '
            f'| Select-Object -First 1 -ExpandProperty Source'
        )
        result = subprocess.run(
            ["powershell", "-Command", search_cmd],
            capture_output=True, text=True
        )

        if result.stdout.strip():
            found = result.stdout.strip()
            launch_cmd = f'Start-Process "{found}" {("-ArgumentList " + arguments) if arguments else ""}'
            subprocess.run(["powershell", "-Command", launch_cmd], capture_output=True)
            return f"Launched: {found}"

        # Case 4: Fallback — try Start-Process directly by name
        fallback_cmd = f'Start-Process "{app_path_or_name}" {("-ArgumentList " + arguments) if arguments else ""}'
        subprocess.Popen(["powershell", "-Command", fallback_cmd])
        return f"Attempted to launch '{app_path_or_name}' (path not verified — confirm manually)."

    except Exception as e:
        return f"Failed to open application: {e}"


# ─────────────────────────────────────────────
# TOOL 3 — Kill Process
# ─────────────────────────────────────────────

@tool
def kill_process(process_name_or_pid: str) -> str:
    """
    Forcibly terminate a running process by name or PID.

    Use this tool when the user wants to:
      - Close/kill/stop/force-quit an application
      - Terminate a frozen or unresponsive program
      - Kill a background process

    ⚠️ DANGEROUS: Killing system processes (e.g., explorer.exe, winlogon.exe,
    lsass.exe, svchost.exe) can cause system instability or data loss.
    Never kill system-critical processes unless the user explicitly confirms.

    Args:
        process_name_or_pid:
            - Process name (partial match): "chrome", "discord", "notepad.exe"
            - Numeric PID: "4521"

    Returns:
        List of processes killed, or an error if none found.
    """
    PROTECTED = {"winlogon.exe", "lsass.exe", "csrss.exe", "smss.exe", "wininit.exe", "services.exe"}

    try:
        killed = []

        # Kill by PID
        if process_name_or_pid.isdigit():
            pid = int(process_name_or_pid)
            proc = psutil.Process(pid)
            name = proc.name()
            if name.lower() in PROTECTED:
                return f"⛔ Refused to kill '{name}' — it is a protected system process."
            proc.kill()
            return f"Killed: {name} (PID {pid})"

        # Kill by name (partial match)
        search_term = process_name_or_pid.lower()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if search_term in pname:
                    if pname in PROTECTED:
                        killed.append(f"⛔ SKIPPED {proc.info['name']} (protected system process)")
                        continue
                    proc.kill()
                    killed.append(f"{proc.info['name']} (PID {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed:
            return f"Killed {len([k for k in killed if '⛔' not in k])} process(es):\n" + "\n".join(killed)
        return f"No processes found matching '{process_name_or_pid}'."

    except psutil.NoSuchProcess:
        return f"Process not found: {process_name_or_pid}"
    except Exception as e:
        return f"Error killing process: {e}"


# ─────────────────────────────────────────────
# TOOL 4 — List Running Processes
# ─────────────────────────────────────────────

@tool
def list_running_processes(filter_term: str = "", sort_by: str = "memory") -> str:
    """
    List currently running processes with CPU and memory usage.

    Use this tool when the user wants to:
      - See what programs/apps are currently running
      - Find the PID of a specific process
      - Identify what's consuming high CPU or RAM
      - Check if a specific application is running

    Args:
        filter_term: Optional. Filter results by process name (partial match).
                     Leave empty to list the top resource-consuming processes.
        sort_by: 'memory' (default) or 'cpu' — determines sort order of results.

    Returns:
        Top 25 matching processes sorted by the specified metric.
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name'] or ""
                if filter_term and filter_term.lower() not in name.lower():
                    continue
                processes.append({
                    "name": name,
                    "pid": proc.info['pid'],
                    "cpu": proc.info['cpu_percent'] or 0.0,
                    "mem": proc.info['memory_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not processes:
            return f"No processes found matching '{filter_term}'."

        key = "mem" if sort_by == "memory" else "cpu"
        processes.sort(key=lambda x: x[key], reverse=True)

        lines = [f"{'NAME':<32} {'PID':<8} {'CPU%':<8} {'MEM%':<8}"]
        lines.append("─" * 58)
        for p in processes[:25]:
            lines.append(
                f"{p['name']:<32} {p['pid']:<8} {p['cpu']:<8.1f} {p['mem']:<8.2f}"
            )

        total = len(processes)
        lines.append(f"\nShowing top 25 of {total} matching process(es). Sorted by {sort_by}.")
        return "\n".join(lines)

    except Exception as e:
        return f"Error listing processes: {e}"


# ─────────────────────────────────────────────
# TOOL 5 — System Power Control
# ─────────────────────────────────────────────

@tool
def system_power_control(action: str) -> str:
    """
    Control the system's power state.

    Use this tool when the user wants to:
      - Shut down or turn off the PC        → action='shutdown'
      - Restart or reboot the PC            → action='restart'
      - Put the PC to sleep                 → action='sleep'
      - Lock the screen/workstation         → action='lock'
      - Sign out / log off the current user → action='logout'

    ⚠️ DESTRUCTIVE: 'shutdown' and 'restart' will immediately close all apps
    and unsaved work will be lost. These require explicit user confirmation
    before calling. 'sleep', 'lock', and 'logout' are considered safe.

    Args:
        action: One of 'shutdown', 'restart', 'sleep', 'lock', 'logout'.

    Returns:
        Confirmation that the action was executed, or an error.
    """
    actions = {
        "shutdown": "shutdown /s /t 5",
        "restart":  "shutdown /r /t 5",
        "sleep":    "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
        "lock":     "rundll32.exe user32.dll,LockWorkStation",
        "logout":   "shutdown /l"
    }

    action = action.lower().strip()
    if action not in actions:
        return f"Invalid action '{action}'. Valid options: {', '.join(actions.keys())}"

    try:
        subprocess.run(actions[action], shell=True)
        if action in ("shutdown", "restart"):
            return f"✅ {action.capitalize()} initiated. System will {action} in 5 seconds."
        return f"✅ {action.capitalize()} executed."
    except Exception as e:
        return f"Error executing {action}: {e}"


# ─────────────────────────────────────────────
# TOOL 6 — Get System Info
# ─────────────────────────────────────────────

@tool
def get_system_info() -> str:
    """
    Retrieve a full snapshot of current system resource usage.

    Use this tool when the user wants to:
      - Check how much RAM/CPU/disk is being used
      - Get an overview of system health/performance
      - Find out total vs. available memory or disk space
      - Check network I/O stats
      - Know the system hostname, OS, uptime, or CPU core count

    No arguments required.

    Returns:
        Formatted report covering CPU, RAM, Disk (C:), Network, and OS metadata.
    """
    try:
        import platform, socket, time

        cpu_count   = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        memory      = psutil.virtual_memory()
        swap        = psutil.swap_memory()

        # Disk — try C: first, fall back to /
        try:
            disk = psutil.disk_usage("C:\\")
        except Exception:
            disk = psutil.disk_usage("/")

        net      = psutil.net_io_counters()
        boot_ts  = psutil.boot_time()
        uptime_s = time.time() - boot_ts
        uptime_h = int(uptime_s // 3600)
        uptime_m = int((uptime_s % 3600) // 60)

        def gb(b): return round(b / (1024 ** 3), 2)

        report = f"""
╔══════════════════════════════════════╗
║         SYSTEM SNAPSHOT              ║
╚══════════════════════════════════════╝

🖥️  OS:       {platform.system()} {platform.release()} ({platform.version()[:40]})
🔖  Host:     {socket.gethostname()}
⏱️  Uptime:   {uptime_h}h {uptime_m}m

⚙️  CPU:      {cpu_percent}% used  ({cpu_count} logical cores)

🧠  RAM:      {memory.percent}% used
              {gb(memory.used)} GB used / {gb(memory.total)} GB total
              {gb(memory.available)} GB available
    Swap:     {gb(swap.used)} GB used / {gb(swap.total)} GB total

💾  Disk (C:) {disk.percent}% used
              {gb(disk.used)} GB used / {gb(disk.total)} GB total
              {gb(disk.free)} GB free

🌐  Network:  Sent     {gb(net.bytes_sent)} GB
              Received {gb(net.bytes_recv)} GB
""".strip()

        return report

    except Exception as e:
        return f"Error retrieving system info: {e}"


# ─────────────────────────────────────────────
# TOOL 7 — Manage Window
# ─────────────────────────────────────────────

@tool
def manage_window(action: str, window_title: str = "") -> str:
    """
    List open windows or perform basic window management actions.

    Use this tool when the user wants to:
      - See what windows are currently open              → action='list'
      - Bring a window to the foreground / focus it      → action='focus'
      - Minimize a window                                → action='minimize'
      - Maximize a window                                → action='maximize'
      - Close a window (graceful, not force-kill)        → action='close'

    NOTE: 'focus', 'minimize', 'maximize', 'close' require the pywin32
    library to be installed. If not available, use execute_command with
    a PowerShell script as a fallback for window manipulation.

    Args:
        action: 'list', 'focus', 'minimize', 'maximize', or 'close'.
        window_title: Partial title of the target window (case-insensitive).
                      Required for all actions except 'list'.

    Returns:
        List of windows for 'list', or confirmation/error for other actions.
    """
    try:
        if action == "list":
            cmd = (
                "Get-Process | Where-Object { $_.MainWindowTitle -ne '' } "
                "| Select-Object Id, ProcessName, MainWindowTitle "
                "| Format-Table -AutoSize"
            )
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True, text=True
            )
            output = result.stdout.strip()
            return f"Open windows:\n{output}" if output else "No windows with titles found."

        # Actions that require pywin32
        try:
            import win32gui
            import win32con

            action_map = {
                "minimize": win32con.SW_MINIMIZE,
                "maximize": win32con.SW_MAXIMIZE,
                "focus":    win32con.SW_RESTORE,
            }

            matched_hwnd = []

            def enum_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        matched_hwnd.append((hwnd, title))

            win32gui.EnumWindows(enum_callback, None)

            if not matched_hwnd:
                return f"No open window found with title matching '{window_title}'."

            hwnd, title = matched_hwnd[0]

            if action == "close":
                import win32con as wc
                win32gui.PostMessage(hwnd, wc.WM_CLOSE, 0, 0)
                return f"Sent close signal to window: '{title}'"
            elif action in action_map:
                import win32gui as wg
                wg.ShowWindow(hwnd, action_map[action])
                wg.SetForegroundWindow(hwnd)
                return f"Applied '{action}' to window: '{title}'"
            else:
                return f"Unknown action '{action}'. Use: list, focus, minimize, maximize, close."

        except ImportError:
            # pywin32 not installed — PowerShell fallback
            ps_action = {
                "close":    f"(Get-Process | Where-Object {{$_.MainWindowTitle -like '*{window_title}*'}}).CloseMainWindow()",
                "minimize": f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class Win32{{[DllImport(\"user32.dll\")]public static extern bool ShowWindow(IntPtr h,int c);}};$p=(Get-Process | Where {{$_.MainWindowTitle -like \"*{window_title}*\"}})|Select -First 1;[Win32]::ShowWindow($p.MainWindowHandle,2)",
                "maximize": f"Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;public class Win32{{[DllImport(\"user32.dll\")]public static extern bool ShowWindow(IntPtr h,int c);}};$p=(Get-Process | Where {{$_.MainWindowTitle -like \"*{window_title}*\"}})|Select -First 1;[Win32]::ShowWindow($p.MainWindowHandle,3)",
            }
            if action in ps_action:
                result = subprocess.run(
                    ["powershell", "-Command", ps_action[action]],
                    capture_output=True, text=True
                )
                return f"Attempted '{action}' on '{window_title}' via PowerShell.\n{result.stdout or result.stderr}"
            return f"pywin32 not installed and no PowerShell fallback for action '{action}'. Install pywin32 for full window control."

    except Exception as e:
        return f"Error managing window: {e}"