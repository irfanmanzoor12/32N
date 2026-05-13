import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from tasks_mcp.store import store
from tasks_mcp.notifications_client import notify_task_finished


async def test_notify_posts_correct_payload():
    task = store.add(user_id="u1", title="Finish me")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=MagicMock(status_code=202))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        await notify_task_finished(task)

    mock_client.post.assert_called_once()
    _, kwargs = mock_client.post.call_args
    payload = kwargs["json"]
    assert payload["event"] == "task.finished"
    assert payload["task_id"] == task.id
    assert payload["user_id"] == task.user_id
    assert payload["title"] == task.title


async def test_notify_does_not_raise_on_connection_error():
    task = store.add(user_id="u1", title="Resilient task")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        await notify_task_finished(task)  # must not raise


async def test_notify_uses_env_url(monkeypatch):
    monkeypatch.setenv("NOTIFICATIONS_API_URL", "http://notifications-api:8001")
    task = store.add(user_id="u1", title="Env URL task")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=MagicMock(status_code=202))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        import importlib
        import tasks_mcp.notifications_client as nc
        importlib.reload(nc)
        from tasks_mcp.notifications_client import notify_task_finished as ntf
        await ntf(task)

    url_called = mock_client.post.call_args[0][0]
    assert url_called.startswith("http://notifications-api:8001")
