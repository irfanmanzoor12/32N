import pytest
from tasks_mcp.store import store


@pytest.fixture(autouse=True)
def reset_store():
    store.clear()
    yield
    store.clear()
