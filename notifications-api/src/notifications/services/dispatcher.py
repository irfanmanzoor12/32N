import logging
import uuid
from abc import ABC, abstractmethod

from notifications.schemas import NotificationRequest, NotificationResult

logger = logging.getLogger(__name__)


class BaseDispatcher(ABC):
    @abstractmethod
    def dispatch(self, request: NotificationRequest) -> NotificationResult:
        ...


class LogDispatcher(BaseDispatcher):
    def dispatch(self, request: NotificationRequest) -> NotificationResult:
        notification_id = str(uuid.uuid4())
        logger.info(
            "notification dispatched event=%s task_id=%s user_id=%s notification_id=%s",
            request.event.value,
            request.task_id,
            request.user_id,
            notification_id,
        )
        return NotificationResult(notification_id=notification_id, accepted=True)
