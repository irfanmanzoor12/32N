"""
E2E tests using MCP in-process memory transport.
Full MCP protocol round-trips without a network hop.
"""
import json
from contextlib import asynccontextmanager
from datetime import date, timedelta
import pytest
from mcp.shared.memory import create_connected_server_and_client_session
from mcp import ClientSession
from tasks_mcp.server import mcp
from tasks_mcp.store import store


@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()


@asynccontextmanager
async def session() -> ClientSession:
    async with create_connected_server_and_client_session(mcp) as client:
        await client.initialize()
        yield client


async def call(client: ClientSession, tool: str, **kwargs):
    result = await client.call_tool(tool, kwargs)
    return json.loads(result.content[0].text)


async def call_raw(client: ClientSession, tool: str, **kwargs) -> str:
    result = await client.call_tool(tool, kwargs)
    return result.content[0].text


# ── Scenario 1: full lifecycle add → finish ────────────────────────────────────
async def test_full_lifecycle_add_then_finish():
    async with session() as client:
        added = await call(client, "tasks_add", title="Write tests", user_id="u1")
        task_id = added["task"]["id"]
        assert added["task"]["status"] == "active"

        finished = await call(client, "tasks_finish", task_id=task_id, user_id="u1")
        assert finished["task"]["status"] == "complete"
        assert finished["task"]["completed_at"] is not None


# ── Scenario 2: full cancel lifecycle ─────────────────────────────────────────
async def test_full_lifecycle_add_then_cancel():
    async with session() as client:
        added = await call(client, "tasks_add", title="Abandoned task", user_id="u1")
        task_id = added["task"]["id"]

        cancelled = await call(client, "tasks_cancel", task_id=task_id, user_id="u1", reason="No longer needed")
        assert cancelled["task"]["status"] == "cancelled"
        assert cancelled["task"]["cancel_reason"] == "No longer needed"


# ── Scenario 3: ownership isolation ──────────────────────────────────────────
async def test_ownership_isolation():
    async with session() as client:
        added = await call(client, "tasks_add", title="Private task", user_id="u1")
        task_id = added["task"]["id"]

        result_text = await call_raw(client, "tasks_get", task_id=task_id, user_id="u2")
        assert "not found" in result_text.lower()


# ── Scenario 4: default user ──────────────────────────────────────────────────
async def test_default_user_isolation():
    async with session() as client:
        await call(client, "tasks_add", title="Default user task")

        listed = await call(client, "tasks_list")
        assert listed["total"] == 1
        assert listed["tasks"][0]["user_id"] == "default"


# ── Scenario 5: tasks_focus sorted overdue + today ────────────────────────────
async def test_focus_returns_correct_tasks_sorted():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    async with session() as client:
        await call(client, "tasks_add", title="Overdue", user_id="u1",
                   due_date=yesterday.isoformat(), priority="low")
        await call(client, "tasks_add", title="Today High", user_id="u1",
                   due_date=today.isoformat(), priority="high")
        await call(client, "tasks_add", title="Tomorrow", user_id="u1",
                   due_date=tomorrow.isoformat())

        focused = await call(client, "tasks_focus", user_id="u1")
        assert focused["overdue_count"] == 1
        assert focused["due_today_count"] == 1
        assert len(focused["tasks"]) == 2
        assert focused["tasks"][0]["priority"] == "high"


# ── Scenario 6: tasks_search by title and notes ───────────────────────────────
async def test_search_finds_by_title_and_notes():
    async with session() as client:
        await call(client, "tasks_add", title="Call Alice", user_id="u1")
        await call(client, "tasks_add", title="Meeting", user_id="u1",
                   notes="Discuss roadmap with Bob")

        alice = await call(client, "tasks_search", query="Alice", user_id="u1")
        assert alice["total"] == 1

        bob = await call(client, "tasks_search", query="Bob", user_id="u1")
        assert bob["total"] == 1


# ── Scenario 7: tasks_list pagination ─────────────────────────────────────────
async def test_list_pagination():
    async with session() as client:
        for i in range(5):
            await call(client, "tasks_add", title=f"Task {i}", user_id="u1")

        page1 = await call(client, "tasks_list", user_id="u1", limit=2, offset=0)
        assert len(page1["tasks"]) == 2
        assert page1["has_more"] is True
        assert page1["next_offset"] == 2

        page3 = await call(client, "tasks_list", user_id="u1", limit=2, offset=4)
        assert len(page3["tasks"]) == 1
        assert page3["has_more"] is False


# ── Scenario 8: tasks_defer then tasks_list with due_before ───────────────────
async def test_defer_then_list_with_due_before():
    future = (date.today() + timedelta(days=30)).isoformat()
    far_future = (date.today() + timedelta(days=60)).isoformat()
    near = (date.today() + timedelta(days=1)).isoformat()

    async with session() as client:
        added = await call(client, "tasks_add", title="Deferrable task", user_id="u1")
        task_id = added["task"]["id"]

        await call(client, "tasks_defer", task_id=task_id, user_id="u1", to_date=future)

        found = await call(client, "tasks_list", user_id="u1", due_before=far_future)
        assert any(t["id"] == task_id for t in found["tasks"])

        not_found = await call(client, "tasks_list", user_id="u1", due_before=near)
        assert not any(t["id"] == task_id for t in not_found["tasks"])


# ── Scenario 9: tasks_update then tasks_get reflects changes ──────────────────
async def test_update_then_get():
    async with session() as client:
        added = await call(client, "tasks_add", title="Original title", user_id="u1")
        task_id = added["task"]["id"]

        await call(client, "tasks_update", task_id=task_id, user_id="u1",
                   changes={"title": "Updated title", "priority": "high"})

        fetched = await call(client, "tasks_get", task_id=task_id, user_id="u1")
        assert fetched["task"]["title"] == "Updated title"
        assert fetched["task"]["priority"] == "high"


# ── Scenario 10: tasks_finish is idempotent ────────────────────────────────────
async def test_finish_idempotent():
    async with session() as client:
        added = await call(client, "tasks_add", title="Deploy to prod", user_id="u1")
        task_id = added["task"]["id"]

        first = await call(client, "tasks_finish", task_id=task_id, user_id="u1")
        second = await call(client, "tasks_finish", task_id=task_id, user_id="u1")
        assert first["task"]["status"] == "complete"
        assert second["task"]["status"] == "complete"
        assert first["task"]["completed_at"] == second["task"]["completed_at"]
