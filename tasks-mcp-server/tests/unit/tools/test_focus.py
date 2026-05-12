import json
from datetime import date, timedelta
from tasks_mcp.store import store
from tasks_mcp.tools.focus import tasks_focus


TODAY = date.today()
YESTERDAY = date.today() - timedelta(days=1)
TOMORROW = date.today() + timedelta(days=1)


async def test_focus_returns_due_today():
    store.add(user_id="u1", title="Today task", due_date=TODAY)
    store.add(user_id="u1", title="Tomorrow task", due_date=TOMORROW)
    data = json.loads(await tasks_focus(user_id="u1"))
    assert data["due_today_count"] == 1
    assert data["tasks"][0]["title"] == "Today task"


async def test_focus_includes_overdue():
    store.add(user_id="u1", title="Overdue task", due_date=YESTERDAY)
    data = json.loads(await tasks_focus(user_id="u1"))
    assert data["overdue_count"] == 1


async def test_focus_sorts_high_priority_first():
    store.add(user_id="u1", title="Low", due_date=TODAY, priority="low")
    store.add(user_id="u1", title="High", due_date=TODAY, priority="high")
    data = json.loads(await tasks_focus(user_id="u1"))
    assert data["tasks"][0]["priority"] == "high"


async def test_focus_excludes_no_due_date():
    store.add(user_id="u1", title="No date task")
    data = json.loads(await tasks_focus(user_id="u1"))
    assert data["due_today_count"] == 0
    assert data["overdue_count"] == 0


async def test_focus_returns_date_used():
    data = json.loads(await tasks_focus(user_id="u1"))
    assert data["date"] == TODAY.isoformat()
