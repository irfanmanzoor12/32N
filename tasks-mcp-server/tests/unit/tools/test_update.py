import json
from tasks_mcp.store import store
from tasks_mcp.tools.update import tasks_update


async def test_update_changes_title():
    task = store.add(user_id="u1", title="Old title")
    data = json.loads(await tasks_update(task_id=task.id, user_id="u1", changes={"title": "New title"}))
    assert data["task"]["title"] == "New title"


async def test_update_clears_due_date_when_null():
    from datetime import date
    task = store.add(user_id="u1", title="Has date", due_date=date(2026, 6, 1))
    data = json.loads(await tasks_update(task_id=task.id, user_id="u1", changes={"due_date": None}))
    assert data["task"]["due_date"] is None


async def test_update_not_found():
    result = await tasks_update(task_id="nope", user_id="u1", changes={"title": "X"})
    assert "not found" in result.lower()


async def test_update_terminal_task_returns_error():
    task = store.add(user_id="u1", title="Done")
    store.update(task.id, status="complete")
    result = await tasks_update(task_id=task.id, user_id="u1", changes={"title": "New"})
    assert "only active tasks" in result.lower()


async def test_update_empty_changes_returns_error():
    task = store.add(user_id="u1", title="Task")
    result = await tasks_update(task_id=task.id, user_id="u1", changes={})
    assert "at least one field" in result.lower()


async def test_update_empty_title_returns_error():
    task = store.add(user_id="u1", title="Task")
    result = await tasks_update(task_id=task.id, user_id="u1", changes={"title": ""})
    assert "cannot be empty" in result.lower()
