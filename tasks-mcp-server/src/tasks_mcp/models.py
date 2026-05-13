from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    active = "active"
    complete = "complete"
    cancelled = "cancelled"


def _require_utc(v: datetime) -> datetime:
    if v.tzinfo is None or v.utcoffset() is None:
        raise ValueError("datetime must be UTC-aware (use timezone.utc)")
    return v


class Task(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    user_id: str
    title: str
    notes: Optional[str] = None
    priority: Priority = Priority.medium
    status: Status = Status.active
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
    completion_note: Optional[str] = None

    @field_validator("created_at", "updated_at", "completed_at", "cancelled_at", mode="before")
    @classmethod
    def must_be_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        return _require_utc(v)
