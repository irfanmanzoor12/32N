from tasks_mcp.store import store, TaskNotFound
from tasks_mcp.tools._helpers import task_response, error_response


async def tasks_get(
    task_id: str,
    user_id: str = "default",
) -> str:
    """Retrieve a single task by ID. Returns not found for missing or wrong-owner tasks."""
    try:
        task = store.get_for_user(task_id, user_id)
        return task_response(task)
    except TaskNotFound:
        return error_response(f"task {task_id} not found")
