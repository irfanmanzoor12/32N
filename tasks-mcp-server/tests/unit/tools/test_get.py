import json
from tasks_mcp.store import store
from tasks_mcp.tools.get import tasks_get


async def test_get_returns_task():
    task = store.add(user_id="u1", title="Find me")
    data = json.loads(await tasks_get(task_id=task.id, user_id="u1"))
    assert data["task"]["id"] == task.id


async def test_get_not_found():
    result = await tasks_get(task_id="nope", user_id="u1")
    assert "not found" in result.lower()


async def test_get_wrong_owner_returns_not_found():
    task = store.add(user_id="u1", title="Private")
    result = await tasks_get(task_id=task.id, user_id="u2")
    assert "not found" in result.lower()
