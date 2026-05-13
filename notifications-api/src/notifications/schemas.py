from enum import Enum
from typing import Any
from pydantic import BaseModel


class EventType(str, Enum):
    task_finished = "task.finished"
    task_cancelled = "task.cancelled"
    task_created = "task.created"
    task_deferred = "task.deferred"


class NotificationRequest(BaseModel):
    event: EventType
    task_id: str
    user_id: str
    title: str
    data: dict[str, Any] = {}


class NotificationResult(BaseModel):
    notification_id: str
    accepted: bool


class NotificationResponse(BaseModel):
    accepted: bool
    event: EventType
    notification_id: str
