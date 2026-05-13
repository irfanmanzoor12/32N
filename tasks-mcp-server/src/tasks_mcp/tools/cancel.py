from datetime import datetime, timezone
from typing import Optional
from tasks_mcp.models import Status
from tasks_mcp.store import store, TaskNotFound
from tasks_mcp.tools._helpers import task_response, error_response


async def tasks_cancel(
    task_id: str,
    user_id: str = "default",
    reason: Optional[str] = None,
) -> str:
    """Cancel a task, preserving it in history. Idempotent."""
    try:
        task = store.get_for_user(task_id, user_id)
    except TaskNotFound:
        return error_response(f"task {task_id} not found")

    if task.status == Status.cancelled:
        return task_response(task)

    if task.status == Status.complete:
        return error_response(f"task {task_id} is already complete")

    store.update(task.id, status=Status.cancelled, cancelled_at=datetime.now(timezone.utc), cancel_reason=reason)
    return task_response(store.get_for_user(task.id, user_id))
