from datetime import datetime, timezone
from typing import Optional
from tasks_mcp.models import Status
from tasks_mcp.store import store, TaskNotFound
from tasks_mcp.tools._helpers import task_response, error_response
from tasks_mcp.notifications_client import notify_task_finished


async def tasks_finish(
    task_id: str,
    user_id: str = "default",
    note: Optional[str] = None,
) -> str:
    """Mark a task as complete. Idempotent — finishing an already-complete task is a no-op."""
    try:
        task = store.get_for_user(task_id, user_id)
    except TaskNotFound:
        return error_response(f"task {task_id} not found")

    if task.status == Status.complete:
        return task_response(task)

    if task.status == Status.cancelled:
        return error_response(
            f"task {task_id} is cancelled and cannot be completed — use tasks_add to create a new task"
        )

    store.update(task.id, status=Status.complete, completed_at=datetime.now(timezone.utc), completion_note=note)
    finished_task = store.get_for_user(task.id, user_id)
    try:
        await notify_task_finished(finished_task)
    except Exception:
        pass
    return task_response(finished_task)
