import json
from typing import Optional
from tasks_mcp.store import store


async def tasks_search(
    query: str,
    user_id: str = "default",
    status: Optional[str] = "active",
    limit: int = 20,
) -> str:
    """Search tasks by title and notes (case-insensitive). query must be at least 2 characters."""
    if len(query) < 2:
        return "query must be at least 2 characters"

    status_filter = None if status == "all" else status
    tasks = store.list(user_id=user_id, status=status_filter)

    needle = query.lower()
    matches = [t for t in tasks if needle in t.title.lower() or (t.notes and needle in t.notes.lower())]
    page = matches[:limit]

    return json.dumps({
        "tasks": [json.loads(t.model_dump_json()) for t in page],
        "total": len(matches),
        "query": query,
    })
