from typing import Any, Optional
from tasks_mcp.models import Status
from tasks_mcp.store import store, TaskNotFound
from tasks_mcp.tools._helpers import task_response, error_response


async def tasks_update(
    task_id: str,
    changes: dict[str, Any],
    user_id: str = "default",
) -> str:
    """Edit task fields (title, notes, priority, due_date). Set due_date to null to clear it.
    Does not change status — use tasks_finish or tasks_cancel for that.
    """
    if not changes:
        return error_response("at least one field must be provided in changes")

    if "title" in changes and changes["title"] == "":
        return error_response("title cannot be empty")

    try:
        task = store.get_for_user(task_id, user_id)
    except TaskNotFound:
        return error_response(f"task {task_id} not found")

    if task.status != Status.active:
        return error_response(f"task {task_id} is {task.status.value} — only active tasks can be updated")

    allowed = {"title", "notes", "priority", "due_date"}
    updates = {k: v for k, v in changes.items() if k in allowed}
    store.update(task.id, **updates)
    return task_response(store.get_for_user(task.id, user_id))
