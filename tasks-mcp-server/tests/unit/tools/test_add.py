import json
import pytest
from tasks_mcp.tools.add import tasks_add


async def test_add_returns_task():
    data = json.loads(await tasks_add(title="Buy milk", user_id="u1"))
    assert data["task"]["title"] == "Buy milk"
    assert data["task"]["status"] == "active"
    assert data["task"]["priority"] == "medium"
    assert data["task"]["user_id"] == "u1"


async def test_add_uses_default_user_id():
    data = json.loads(await tasks_add(title="No user"))
    assert data["task"]["user_id"] == "default"


async def test_add_with_all_fields():
    from datetime import date
    data = json.loads(await tasks_add(
        title="Call John", notes="Re: contract",
        due_date=date(2026, 6, 1), priority="high", user_id="u1",
    ))
    t = data["task"]
    assert t["notes"] == "Re: contract"
    assert t["due_date"] == "2026-06-01"
    assert t["priority"] == "high"


async def test_add_rejects_empty_title():
    result = await tasks_add(title="", user_id="u1")
    assert "required" in result.lower()


async def test_add_trims_title_whitespace():
    data = json.loads(await tasks_add(title="  Trim me  "))
    assert data["task"]["title"] == "Trim me"
