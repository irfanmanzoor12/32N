from datetime import date
from tasks_mcp.models import Status
from tasks_mcp.store import store, TaskNotFound
from tasks_mcp.tools._helpers import task_response, error_response


async def tasks_defer(
    task_id: str,
    to_date: date,
    user_id: str = "default",
) -> str:
    """Move a task's due date forward. to_date must be today or a future date."""
    try:
        task = store.get_for_user(task_id, user_id)
    except TaskNotFound:
        return error_response(f"task {task_id} not found")

    if task.status != Status.active:
        return error_response(f"task {task_id} is {task.status.value} — only active tasks can be deferred")

    if to_date < date.today():
        return error_response("to_date must be today or a future date")

    store.update(task.id, due_date=to_date)
    return task_response(store.get_for_user(task.id, user_id))
