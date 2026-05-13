from fastapi import APIRouter, Depends

from notifications.schemas import NotificationRequest, NotificationResponse
from notifications.services.dispatcher import BaseDispatcher, LogDispatcher

router = APIRouter(tags=["notifications"])


def get_dispatcher() -> BaseDispatcher:
    return LogDispatcher()


@router.post("/notify", response_model=NotificationResponse, status_code=202)
def notify(
    request: NotificationRequest,
    dispatcher: BaseDispatcher = Depends(get_dispatcher),
) -> NotificationResponse:
    result = dispatcher.dispatch(request)
    return NotificationResponse(
        accepted=result.accepted,
        event=request.event,
        notification_id=result.notification_id,
    )
