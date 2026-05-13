import pytest
from tasks_mcp.store import TaskStore, TaskNotFound


@pytest.fixture
def store() -> TaskStore:
    return TaskStore()


def test_add_returns_task_with_uuid(store):
    task = store.add(user_id="u1", title="Buy milk")
    assert task.id
    assert task.title == "Buy milk"
    assert task.user_id == "u1"


def test_add_sets_utc_timestamps(store):
    from datetime import timezone
    task = store.add(user_id="u1", title="Check time")
    assert task.created_at.tzinfo == timezone.utc
    assert task.updated_at.tzinfo == timezone.utc


def test_get_for_user_returns_own_task(store):
    task = store.add(user_id="u1", title="My task")
    fetched = store.get_for_user(task.id, "u1")
    assert fetched.id == task.id


def test_get_for_user_raises_for_missing_task(store):
    with pytest.raises(TaskNotFound):
        store.get_for_user("nonexistent-id", "u1")


def test_get_for_user_raises_for_wrong_owner(store):
    task = store.add(user_id="u1", title="Secret task")
    with pytest.raises(TaskNotFound):
        store.get_for_user(task.id, "u2")


def test_list_returns_only_user_tasks(store):
    store.add(user_id="u1", title="Task A")
    store.add(user_id="u1", title="Task B")
    store.add(user_id="u2", title="Other user task")
    tasks = store.list(user_id="u1")
    assert len(tasks) == 2
    assert all(t.user_id == "u1" for t in tasks)


def test_update_persists_changes_and_bumps_updated_at(store):
    import time
    task = store.add(user_id="u1", title="Original")
    original_updated_at = task.updated_at
    time.sleep(0.01)
    updated = store.update(task.id, title="Updated")
    assert updated.title == "Updated"
    assert updated.updated_at > original_updated_at


def test_clear_empties_store(store):
    store.add(user_id="u1", title="Task")
    store.clear()
    assert store.list(user_id="u1") == []
