from datetime import date, datetime, timezone
import pytest
from pydantic import ValidationError
from tasks_mcp.models import Priority, Status, Task


def make_task(**kwargs) -> Task:
    defaults = dict(
        id="abc-123",
        user_id="u1",
        title="Test task",
        priority=Priority.medium,
        status=Status.active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return Task(**(defaults | kwargs))


def test_task_created_with_required_fields():
    t = make_task()
    assert t.title == "Test task"
    assert t.priority == Priority.medium
    assert t.status == Status.active
    assert t.user_id == "u1"


def test_created_at_must_be_utc():
    naive = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ValidationError):
        make_task(created_at=naive)


def test_updated_at_must_be_utc():
    naive = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ValidationError):
        make_task(updated_at=naive)


def test_due_date_accepts_date_only():
    t = make_task(due_date=date(2026, 5, 20))
    assert t.due_date == date(2026, 5, 20)


def test_optional_fields_default_none():
    t = make_task()
    assert t.notes is None
    assert t.due_date is None
    assert t.completed_at is None
    assert t.cancelled_at is None
    assert t.cancel_reason is None
    assert t.completion_note is None


def test_priority_enum_values():
    assert Priority.low == "low"
    assert Priority.medium == "medium"
    assert Priority.high == "high"


def test_status_enum_values():
    assert Status.active == "active"
    assert Status.complete == "complete"
    assert Status.cancelled == "cancelled"
