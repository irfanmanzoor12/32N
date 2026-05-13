import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from notifications.config import settings
from notifications.routers.health import router as health_router
from notifications.routers.notify import router as notify_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("notifications-api starting")
    yield
    logger.info("notifications-api stopping")


app = FastAPI(
    title="Notifications API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(notify_router)
