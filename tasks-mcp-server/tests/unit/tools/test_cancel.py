import json
from tasks_mcp.store import store
from tasks_mcp.tools.cancel import tasks_cancel


async def test_cancel_sets_status():
    task = store.add(user_id="u1", title="Old plan")
    data = json.loads(await tasks_cancel(task_id=task.id, user_id="u1"))
    assert data["task"]["status"] == "cancelled"
    assert data["task"]["cancelled_at"] is not None


async def test_cancel_stores_reason():
    task = store.add(user_id="u1", title="Trip")
    data = json.loads(await tasks_cancel(task_id=task.id, user_id="u1", reason="Plans changed"))
    assert data["task"]["cancel_reason"] == "Plans changed"


async def test_cancel_is_idempotent():
    task = store.add(user_id="u1", title="Dup")
    await tasks_cancel(task_id=task.id, user_id="u1")
    data = json.loads(await tasks_cancel(task_id=task.id, user_id="u1"))
    assert data["task"]["status"] == "cancelled"


async def test_cancel_not_found():
    result = await tasks_cancel(task_id="nope", user_id="u1")
    assert "not found" in result.lower()


async def test_cancel_already_complete_returns_error():
    task = store.add(user_id="u1", title="Done task")
    store.update(task.id, status="complete")
    result = await tasks_cancel(task_id=task.id, user_id="u1")
    assert "already complete" in result.lower()
