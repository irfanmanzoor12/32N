import json
from tasks_mcp.store import store
from tasks_mcp.tools.list import tasks_list


async def test_list_returns_active_by_default():
    store.add(user_id="u1", title="Active")
    t = store.add(user_id="u1", title="Done")
    store.update(t.id, status="complete")
    data = json.loads(await tasks_list(user_id="u1"))
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Active"


async def test_list_filters_by_status():
    store.add(user_id="u1", title="Active")
    t = store.add(user_id="u1", title="Done")
    store.update(t.id, status="complete")
    data = json.loads(await tasks_list(user_id="u1", status="complete"))
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Done"


async def test_list_filters_by_priority():
    store.add(user_id="u1", title="Low", priority="low")
    store.add(user_id="u1", title="High", priority="high")
    data = json.loads(await tasks_list(user_id="u1", priority="high", status="all"))
    assert all(t["priority"] == "high" for t in data["tasks"])


async def test_list_pagination():
    for i in range(5):
        store.add(user_id="u1", title=f"Task {i}")
    data = json.loads(await tasks_list(user_id="u1", limit=2, offset=0))
    assert len(data["tasks"]) == 2
    assert data["has_more"] is True
    assert data["next_offset"] == 2


async def test_list_uses_default_user():
    store.add(user_id="default", title="Default task")
    data = json.loads(await tasks_list())
    assert data["total"] == 1


async def test_list_isolates_users():
    store.add(user_id="u1", title="U1 task")
    store.add(user_id="u2", title="U2 task")
    data = json.loads(await tasks_list(user_id="u1"))
    assert data["total"] == 1
