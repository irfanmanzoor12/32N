import json
from tasks_mcp.store import store
from tasks_mcp.tools.finish import tasks_finish


async def test_finish_completes_task():
    task = store.add(user_id="u1", title="Write report")
    data = json.loads(await tasks_finish(task_id=task.id, user_id="u1"))
    assert data["task"]["status"] == "complete"
    assert data["task"]["completed_at"] is not None


async def test_finish_with_note():
    task = store.add(user_id="u1", title="Review PR")
    data = json.loads(await tasks_finish(task_id=task.id, user_id="u1", note="LGTM"))
    assert data["task"]["completion_note"] == "LGTM"


async def test_finish_is_idempotent():
    task = store.add(user_id="u1", title="Deploy")
    await tasks_finish(task_id=task.id, user_id="u1")
    data = json.loads(await tasks_finish(task_id=task.id, user_id="u1"))
    assert data["task"]["status"] == "complete"


async def test_finish_not_found():
    result = await tasks_finish(task_id="bad-id", user_id="u1")
    assert "not found" in result.lower()


async def test_finish_cancelled_task_returns_error():
    task = store.add(user_id="u1", title="Old task")
    store.update(task.id, status="cancelled")
    result = await tasks_finish(task_id=task.id, user_id="u1")
    assert "cancelled" in result.lower()


async def test_finish_uses_default_user():
    task = store.add(user_id="default", title="Default user task")
    data = json.loads(await tasks_finish(task_id=task.id))
    assert data["task"]["status"] == "complete"
