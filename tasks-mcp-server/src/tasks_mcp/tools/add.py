from datetime import date
from typing import Optional
from tasks_mcp.models import Priority
from tasks_mcp.store import store
from tasks_mcp.tools._helpers import task_response


async def tasks_add(
    title: str,
    user_id: str = "default",
    notes: Optional[str] = None,
    due_date: Optional[date] = None,
    priority: Priority = Priority.medium,
) -> str:
    """Create a new task. Use when the user wants to add something to their list."""
    if not title or not title.strip():
        return "title is required and cannot be empty"
    task = store.add(
        user_id=user_id,
        title=title.strip(),
        notes=notes,
        due_date=due_date,
        priority=priority,
    )
    return task_response(task)
