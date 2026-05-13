# Notifications API — Implementation Plan

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12+ |
| Package manager | uv |
| Framework | FastAPI |
| Validation | Pydantic v2 (via FastAPI) |
| Settings | pydantic-settings |
| Test runner | pytest |
| HTTP test client | httpx (via FastAPI TestClient) |
| Port | 8001 |

---

## Project Location

```
notifications-api/          ← sibling to tasks-mcp-server
```

---

## Project Structure

```
notifications-api/
├── pyproject.toml
├── src/
│   └── notifications/
│       ├── __init__.py
│       ├── main.py          # FastAPI app, lifespan, mounts routers
│       ├── config.py        # Settings via pydantic-settings
│       ├── schemas.py       # NotificationRequest, NotificationResponse, EventType
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── health.py    # GET /health/live, GET /health/ready
│       │   └── notify.py    # POST /notify
│       └── services/
│           ├── __init__.py
│           └── dispatcher.py  # BaseDispatcher ABC + LogDispatcher
└── tests/
    ├── __init__.py
    ├── conftest.py           # client fixture, mock_dispatcher fixture
    ├── test_health.py
    └── test_notify.py
```

---

## API

### POST /notify

**Request**
```json
{
  "event": "task.finished",
  "task_id": "uuid",
  "user_id": "user1",
  "title": "Buy groceries",
  "data": {}
}
```

**Response** `202 Accepted`
```json
{
  "accepted": true,
  "event": "task.finished",
  "notification_id": "uuid"
}
```

**Errors**
| Condition | Status |
|---|---|
| Unknown event type | 422 |
| Missing required field | 422 |

### GET /health/live → `200 { "status": "ok" }`
### GET /health/ready → `200 { "status": "ok" }`

---

## Layer Responsibilities

### `schemas.py`
- `EventType` enum: `task.finished | task.cancelled | task.created | task.deferred`
- `NotificationRequest` — validated inbound payload
- `NotificationResult` — internal return from dispatcher
- `NotificationResponse` — outbound API response

### `services/dispatcher.py`
- `BaseDispatcher` ABC with single `dispatch(request) → NotificationResult` method
- `LogDispatcher` — logs event with structured fields, returns a UUID notification_id
- Channels are added by subclassing `BaseDispatcher` — `notify.py` never changes

### `routers/notify.py`
- Thin route: validates input (Pydantic), calls dispatcher, returns response
- `get_dispatcher()` dependency — overridable in tests

### `routers/health.py`
- `/health/live` — always 200 (process is alive)
- `/health/ready` — 200 when ready to serve traffic (checks deps when they exist)

---

## TDD Order

1. `test_health.py` (failing) → `routers/health.py`
2. `test_notify.py` (failing) → `schemas.py` + `routers/notify.py` + `services/dispatcher.py`

---

## Delivery Gate

- [x] All tests pass: `uv run pytest` — 10/10 passed 2026-05-13
- [x] Server starts: `uv run uvicorn notifications.main:app --port 8001`
- [x] `POST /notify` returns 202 with `notification_id`
- [x] Unknown event returns 422
- [x] `/health/live` and `/health/ready` return 200
- [x] Swagger UI at `http://localhost:8001/docs` → HTTP 200
- [x] No secrets in code or config files
