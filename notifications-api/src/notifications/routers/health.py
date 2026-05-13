from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness() -> dict:
    return {"status": "ok"}
