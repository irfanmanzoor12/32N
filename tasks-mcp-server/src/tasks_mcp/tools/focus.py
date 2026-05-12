import json
from datetime import date
from typing import Optional
from tasks_mcp.models import Priority, Status
from tasks_mcp.store import store

_PRIORITY_ORDER = {Priority.high: 0, Priority.medium: 1, Priority.low: 2}


async def tasks_focus(
    user_id: str = "default",
    focus_date: Optional[date] = None,
) -> str:
    """Return overdue + due-today tasks sorted by priority. Use for 'what should I do now?'"""
    target = focus_date or date.today()
    all_active = store.list(user_id=user_id, status=Status.active)

    overdue = [t for t in all_active if t.due_date is not None and t.due_date < target]
    due_today = [t for t in all_active if t.due_date == target]

    combined = overdue + due_today
    combined.sort(key=lambda t: (_PRIORITY_ORDER[t.priority], t.due_date or date.max))

    return json.dumps({
        "tasks": [json.loads(t.model_dump_json()) for t in combined],
        "date": target.isoformat(),
        "overdue_count": len(overdue),
        "due_today_count": len(due_today),
    })
