import json
import pytest
from tasks_mcp.store import store
from tasks_mcp.tools.search import tasks_search


async def test_search_finds_by_title():
    store.add(user_id="u1", title="Call John about contract")
    data = json.loads(await tasks_search(query="John", user_id="u1"))
    assert data["total"] == 1


async def test_search_finds_by_notes():
    store.add(user_id="u1", title="Meeting", notes="Discuss the roadmap with Alice")
    data = json.loads(await tasks_search(query="Alice", user_id="u1"))
    assert data["total"] == 1


async def test_search_is_case_insensitive():
    store.add(user_id="u1", title="UPPER CASE TASK")
    data = json.loads(await tasks_search(query="upper case", user_id="u1"))
    assert data["total"] == 1


async def test_search_echoes_query():
    data = json.loads(await tasks_search(query="anything", user_id="u1"))
    assert data["query"] == "anything"


async def test_search_min_length():
    result = await tasks_search(query="x", user_id="u1")
    assert "at least 2" in result.lower()


async def test_search_isolates_users():
    store.add(user_id="u1", title="Secret task u1")
    data = json.loads(await tasks_search(query="Secret", user_id="u2"))
    assert data["total"] == 0
