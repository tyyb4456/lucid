"""
LUCID System Control Tools - Full Windows PC Control
Capabilities: Process management, power control, window management, system info
"""

from langchain_core.tools import tool
import subprocess
import psutil
import os
import sys
from pathlib import Path
from typing import Optional

@tool
def execute_command(command: str, shell: str = "powershell") -> str:
    """
    Execute ANY system command (PowerShell, CMD, or Bash).
    EXTREMELY POWERFUL - Can run any command on the system.
    
    Args:
        command: The command to execute
        shell: 'powershell', 'cmd', or 'bash'
    
    Examples:
        "Get-Process | Select-Object -First 10"
        "dir C:\\ /s /b *.txt"
        "netstat -an"
    """
    try:
        if shell == "powershell":
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif shell == "cmd":
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        output = result.stdout if result.stdout else result.stderr
        return f"Command executed:\n{output[:2000]}"  # Limit output
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {e}"


@tool
def open_any_application(app_path_or_name: str, arguments: str = "") -> str:
    """
    Open ANY application on the system by path or search by name.
    Can launch executables, URLs, files with default programs.
    
    Args:
        app_path_or_name: Full path to exe OR application name to search for
        arguments: Command-line arguments to pass
    
    Examples:
        "notepad.exe"
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        "https://youtube.com"
        "Code" (searches for VS Code)
    """
    try:
        # If it's a URL
        if app_path_or_name.startswith("http"):
            import webbrowser
            webbrowser.open(app_path_or_name)
            return f"Opened {app_path_or_name} in default browser"
        
        # If it's a full path
        if Path(app_path_or_name).exists():
            cmd = f'"{app_path_or_name}" {arguments}'
            subprocess.Popen(cmd, shell=True)
            return f"Launched {app_path_or_name}"
        
        # Search for the application
        search_cmd = f'Get-Command "{app_path_or_name}*" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source'
        result = subprocess.run(
            ["powershell", "-Command", search_cmd],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            found_path = result.stdout.strip()
            subprocess.Popen(f'"{found_path}" {arguments}', shell=True)
            return f"Launched {found_path}"
        else:
            # Try direct shell execution
            subprocess.Popen(f"{app_path_or_name} {arguments}", shell=True)
            return f"Attempted to launch {app_path_or_name}"
            
    except Exception as e:
        return f"Failed to open application: {e}"


@tool
def kill_process(process_name_or_pid: str) -> str:
    """
    Kill/terminate any running process by name or PID.
    
    Args:
        process_name_or_pid: Process name (e.g., "chrome.exe") or PID number
    
    Examples:
        "chrome.exe"
        "1234" (PID)
        "discord"
    """
    try:
        killed = []
        
        # Try as PID first
        if process_name_or_pid.isdigit():
            pid = int(process_name_or_pid)
            proc = psutil.Process(pid)
            proc.kill()
            return f"Killed process PID {pid} ({proc.name()})"
        
        # Kill by name
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name_or_pid.lower() in proc.info['name'].lower():
                proc.kill()
                killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
        
        if killed:
            return f"Killed {len(killed)} process(es): " + ", ".join(killed)
        return f"No processes found matching '{process_name_or_pid}'"
    
    except psutil.NoSuchProcess:
        return f"Process {process_name_or_pid} not found"
    except Exception as e:
        return f"Error killing process: {e}"


@tool
def list_running_processes(filter_term: str = "") -> str:
    """
    List all running processes with CPU/Memory usage.
    
    Args:
        filter_term: Optional search term to filter processes
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if filter_term.lower() in proc.info['name'].lower() or not filter_term:
                    processes.append(
                        f"{proc.info['name']:<30} PID:{proc.info['pid']:<8} "
                        f"CPU:{proc.info['cpu_percent']:.1f}% MEM:{proc.info['memory_percent']:.1f}%"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not processes:
            return f"No processes found matching '{filter_term}'"
        
        # Return top 20
        return "Running processes:\n" + "\n".join(processes[:20])
    
    except Exception as e:
        return f"Error listing processes: {e}"


@tool
def system_power_control(action: str) -> str:
    """
    Control system power state.
    
    Args:
        action: 'shutdown', 'restart', 'sleep', 'lock', 'logout'
    
    DANGEROUS - Use with confirmation!
    """
    actions = {
        "shutdown": "shutdown /s /t 0",
        "restart": "shutdown /r /t 0",
        "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
        "lock": "rundll32.exe user32.dll,LockWorkStation",
        "logout": "shutdown /l"
    }
    
    if action.lower() not in actions:
        return f"Invalid action. Choose from: {', '.join(actions.keys())}"
    
    try:
        # Add 10 second delay for shutdown/restart
        if action.lower() in ["shutdown", "restart"]:
            return f"⚠️ SAFETY: I won't actually {action} your PC. Please confirm if you really want this."
        
        subprocess.run(actions[action.lower()], shell=True)
        return f"Executing {action}..."
    except Exception as e:
        return f"Error: {e}"


@tool
def get_system_info() -> str:
    """Get comprehensive system information (CPU, RAM, Disk, Network)."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = f"""
🖥️ System Information:

CPU Usage: {cpu_percent}%
RAM: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
Disk: {disk.percent}% used ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
"""
        return info.strip()
    except Exception as e:
        return f"Error getting system info: {e}"


@tool
def manage_window(action: str, window_title: str = "") -> str:
    """
    Control application windows (minimize, maximize, close, focus).
    
    Args:
        action: 'minimize', 'maximize', 'close', 'focus', 'list'
        window_title: Title or partial title of window to control
    
    Examples:
        action="list" - List all open windows
        action="close", window_title="Chrome"
    """
    try:
        if action == "list":
            # PowerShell to list windows
            cmd = 'Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object MainWindowTitle -Unique'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True
            )
            return f"Open windows:\n{result.stdout}"
        
        return f"Window management requires pywin32 (Windows-specific). Action: {action} on '{window_title}'"
    
    except Exception as e:
        return f"Error managing window: {e}"