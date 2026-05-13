import json
from datetime import date
from typing import Optional
from tasks_mcp.models import Priority, Status
from tasks_mcp.store import store


async def tasks_list(
    user_id: str = "default",
    status: Optional[str] = "active",
    priority: Optional[Priority] = None,
    due_before: Optional[date] = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """List tasks with optional filters. Defaults to active tasks only.
    Use status='all' to include complete and cancelled tasks.
    """
    if limit < 1 or limit > 200:
        return "limit must be between 1 and 200"

    status_filter = None if status == "all" else status
    tasks = store.list(user_id=user_id, status=status_filter, priority=priority, due_before=due_before)
    total = len(tasks)
    page = tasks[offset: offset + limit]
    has_more = (offset + len(page)) < total
    return json.dumps({
        "tasks": [json.loads(t.model_dump_json()) for t in page],
        "total": total,
        "has_more": has_more,
        "next_offset": offset + len(page) if has_more else None,
    })
