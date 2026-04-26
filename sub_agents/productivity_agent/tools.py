"""
LUCID Productivity Tools - TODO lists, notes, task management
"""

from langchain_core.tools import tool
from pathlib import Path
import json
import datetime

TODO_FILE = Path("./data/todos/todos.json")
NOTES_FILE = Path("./data/notes/notes.json")

def _load_todos() -> list:
    """Load todos from JSON file."""
    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]")
    return json.loads(TODO_FILE.read_text())

def _save_todos(todos: list):
    """Save todos to JSON file."""
    TODO_FILE.write_text(json.dumps(todos, indent=2))

def _load_notes() -> list:
    """Load notes from JSON file."""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("[]")
    return json.loads(NOTES_FILE.read_text())

def _save_notes(notes: list):
    """Save notes to JSON file."""
    NOTES_FILE.write_text(json.dumps(notes, indent=2))


@tool
def add_todo(task: str, priority: str = "normal", due_date: str = "") -> str:
    """
    Add a task to your TODO list.
    
    Args:
        task: Task description
        priority: 'high', 'normal', or 'low'
        due_date: Optional due date (YYYY-MM-DD)
    
    Examples:
        task="Finish project report", priority="high"
        task="Buy groceries", due_date="2024-01-20"
    """
    try:
        todos = _load_todos()
        
        todo = {
            "id": len(todos) + 1,
            "task": task,
            "priority": priority.lower(),
            "done": False,
            "created": datetime.datetime.now().isoformat(),
            "due_date": due_date if due_date else None
        }
        
        todos.append(todo)
        _save_todos(todos)
        
        priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(priority.lower(), "🟡")
        
        return f"✅ Task added: {priority_emoji} '{task}' [Priority: {priority}]"
    
    except Exception as e:
        return f"Error adding todo: {e}"


@tool
def read_todos(filter_status: str = "pending") -> str:
    """
    Read your TODO list.
    
    Args:
        filter_status: 'pending', 'completed', or 'all'
    """
    try:
        todos = _load_todos()
        
        if filter_status == "pending":
            filtered = [t for t in todos if not t["done"]]
        elif filter_status == "completed":
            filtered = [t for t in todos if t["done"]]
        else:
            filtered = todos
        
        if not filtered:
            return f"No {filter_status} tasks found."
        
        lines = []
        for i, todo in enumerate(filtered, 1):
            priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(todo["priority"], "🟡")
            status = "✓" if todo["done"] else "○"
            
            task_line = f"{i}. {status} {priority_emoji} {todo['task']}"
            
            if todo.get("due_date"):
                task_line += f" (Due: {todo['due_date']})"
            
            lines.append(task_line)
        
        header = f"📋 TODO List ({filter_status.upper()}) - {len(filtered)} task(s):"
        return header + "\n" + "\n".join(lines)
    
    except Exception as e:
        return f"Error reading todos: {e}"


@tool
def complete_todo(task_number: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        task_number: Task number from the list
    """
    try:
        todos = _load_todos()
        pending = [t for t in todos if not t["done"]]
        
        if task_number < 1 or task_number > len(pending):
            return f"Invalid task number. You have {len(pending)} pending task(s)."
        
        task = pending[task_number - 1]
        
        # Find and update in original list
        for t in todos:
            if t["id"] == task["id"]:
                t["done"] = True
                t["completed_at"] = datetime.datetime.now().isoformat()
        
        _save_todos(todos)
        
        return f"✅ Task completed: '{task['task']}'"
    
    except Exception as e:
        return f"Error completing todo: {e}"


@tool
def delete_todo(task_number: int) -> str:
    """
    Delete a task from the TODO list.
    
    Args:
        task_number: Task number to delete
    """
    try:
        todos = _load_todos()
        pending = [t for t in todos if not t["done"]]
        
        if task_number < 1 or task_number > len(pending):
            return f"Invalid task number. You have {len(pending)} pending task(s)."
        
        task = pending[task_number - 1]
        
        # Remove from original list
        todos = [t for t in todos if t["id"] != task["id"]]
        _save_todos(todos)
        
        return f"🗑️ Task deleted: '{task['task']}'"
    
    except Exception as e:
        return f"Error deleting todo: {e}"


@tool
def clear_completed_todos() -> str:
    """Clear all completed tasks from the TODO list."""
    try:
        todos = _load_todos()
        pending = [t for t in todos if not t["done"]]
        completed_count = len(todos) - len(pending)
        
        _save_todos(pending)
        
        return f"🗑️ Cleared {completed_count} completed task(s). {len(pending)} pending task(s) remain."
    
    except Exception as e:
        return f"Error clearing todos: {e}"


@tool
def create_note(title: str, content: str, tags: str = "") -> str:
    """
    Create a quick note.
    
    Args:
        title: Note title
        content: Note content
        tags: Comma-separated tags (optional)
    """
    try:
        notes = _load_notes()
        
        note = {
            "id": len(notes) + 1,
            "title": title,
            "content": content,
            "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
            "created": datetime.datetime.now().isoformat()
        }
        
        notes.append(note)
        _save_notes(notes)
        
        tags_str = f" [Tags: {tags}]" if tags else ""
        return f"📝 Note saved: '{title}'{tags_str}"
    
    except Exception as e:
        return f"Error creating note: {e}"


@tool
def read_notes(search_term: str = "") -> str:
    """
    Read all notes or search by keyword.
    
    Args:
        search_term: Optional search term to filter notes
    """
    try:
        notes = _load_notes()
        
        if search_term:
            filtered = [
                n for n in notes 
                if search_term.lower() in n["title"].lower() 
                or search_term.lower() in n["content"].lower()
                or any(search_term.lower() in tag.lower() for tag in n.get("tags", []))
            ]
        else:
            filtered = notes
        
        if not filtered:
            return "No notes found." if not search_term else f"No notes found matching '{search_term}'"
        
        lines = []
        for note in filtered:
            tags = f" [{', '.join(note.get('tags', []))}]" if note.get('tags') else ""
            lines.append(f"\n📌 {note['title']}{tags}")
            lines.append(f"   {note['content'][:100]}...")
            lines.append(f"   Created: {note['created'][:10]}")
        
        header = f"📝 Notes ({len(filtered)} found):"
        return header + "\n".join(lines)
    
    except Exception as e:
        return f"Error reading notes: {e}"


@tool
def delete_note(note_id: int) -> str:
    """
    Delete a note by its ID.
    
    Args:
        note_id: ID of the note to delete
    """
    try:
        notes = _load_notes()
        
        note_to_delete = next((n for n in notes if n["id"] == note_id), None)
        
        if not note_to_delete:
            return f"Note with ID {note_id} not found."
        
        notes = [n for n in notes if n["id"] != note_id]
        _save_notes(notes)
        
        return f"🗑️ Note deleted: '{note_to_delete['title']}'"
    
    except Exception as e:
        return f"Error deleting note: {e}"