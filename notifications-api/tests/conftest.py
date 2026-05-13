import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from notifications.main import app
from notifications.routers.notify import get_dispatcher
from notifications.schemas import NotificationResult


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_dispatcher(client):
    mock = MagicMock()
    mock.dispatch.return_value = NotificationResult(
        notification_id="test-notification-id",
        accepted=True,
    )
    app.dependency_overrides[get_dispatcher] = lambda: mock
    yield mock
    app.dependency_overrides.clear()
