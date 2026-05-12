import json
from datetime import date, timedelta
from tasks_mcp.store import store
from tasks_mcp.tools.defer import tasks_defer


async def test_defer_updates_due_date():
    task = store.add(user_id="u1", title="Meeting prep")
    data = json.loads(await tasks_defer(task_id=task.id, user_id="u1", to_date=date(2099, 12, 1)))
    assert data["task"]["due_date"] == "2099-12-01"


async def test_defer_not_found():
    result = await tasks_defer(task_id="nope", user_id="u1", to_date=date(2099, 12, 1))
    assert "not found" in result.lower()


async def test_defer_terminal_task_returns_error():
    task = store.add(user_id="u1", title="Done")
    store.update(task.id, status="complete")
    result = await tasks_defer(task_id=task.id, user_id="u1", to_date=date(2099, 12, 1))
    assert "only active tasks" in result.lower()


async def test_defer_past_date_returns_error():
    task = store.add(user_id="u1", title="Task")
    result = await tasks_defer(task_id=task.id, user_id="u1", to_date=date(2000, 1, 1))
    assert "future date" in result.lower()
