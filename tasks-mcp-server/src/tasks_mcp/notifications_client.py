import logging
import os

import httpx

logger = logging.getLogger(__name__)

NOTIFICATIONS_API_URL = os.getenv("NOTIFICATIONS_API_URL", "http://localhost:8001")


async def notify_task_finished(task) -> None:
    """POST task.finished event to the notifications API. Fire-and-forget — never raises."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(
                f"{NOTIFICATIONS_API_URL}/notify",
                json={
                    "event": "task.finished",
                    "task_id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "data": {"completion_note": task.completion_note},
                },
            )
    except Exception as exc:
        logger.warning("notifications API unreachable — skipping: %s", exc)
