# MCP Server — Implementation Plan

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12+ |
| Package manager | uv |
| MCP framework | FastMCP (via `mcp` package) |
| Validation | Pydantic v2 |
| Test runner | pytest + pytest-asyncio |
| Transport | Streamable HTTP, port 8000 |

---

## Project Location

```
tasks-mcp-server/          ← sibling to other services, not nested
```

---

## Project Structure

```
tasks-mcp-server/
├── pyproject.toml
├── src/
│   └── tasks_mcp/
│       ├── __init__.py
│       ├── server.py          # FastMCP init, registers all tools, sets transport
│       ├── models.py          # Task Pydantic model + Priority/Status enums
│       ├── store.py           # TaskStore — in-memory dict, all read/write operations
│       └── tools/
│           ├── __init__.py
│           ├── add.py
│           ├── finish.py
│           ├── cancel.py
│           ├── defer.py
│           ├── update.py
│           ├── get.py
│           ├── list.py
│           ├── focus.py
│           └── search.py
└── tests/
    ├── conftest.py            # fixtures: fresh_store, mcp_client
    ├── unit/
    │   ├── test_models.py
    │   ├── test_store.py
    │   └── tools/
    │       ├── test_add.py
    │       ├── test_finish.py
    │       ├── test_cancel.py
    │       ├── test_defer.py
    │       ├── test_update.py
    │       ├── test_get.py
    │       ├── test_list.py
    │       ├── test_focus.py
    │       └── test_search.py
    └── e2e/
        └── test_server.py     # full round-trip via MCP Python client over HTTP
```

---

## Dependencies

**Runtime** (`uv add`)
```
mcp[cli]          # FastMCP + MCP Python SDK
pydantic          # v2, input validation
uvicorn           # ASGI server for HTTP transport
```

**Dev** (`uv add --dev`)
```
pytest
pytest-asyncio
httpx             # async HTTP client for e2e tests
```

---

## Layer Responsibilities

### `models.py`
- `Priority` enum: `low | medium | high`
- `Status` enum: `active | complete | cancelled`
- `Task` Pydantic model with all fields from the spec
- UTC enforcement: `created_at`, `updated_at`, and all `*_at` fields use `datetime` with `timezone=UTC`; serialise to ISO 8601 `"Z"` suffix
- `due_date` is `date` (no time, no timezone)

### `store.py`
- `TaskStore` class wrapping `dict[str, Task]`
- Methods: `add`, `get`, `list`, `update`, `delete` (never exposed — used internally by tools)
- Ownership check helper: `get_for_user(task_id, user_id)` — returns task or raises `TaskNotFound`
- Single module-level instance: `store = TaskStore()` — imported by tools

### `tools/*.py`
- One file per tool
- Each file: one Pydantic input model + one `async def` registered with `@mcp.tool`
- Tools call `store` directly — no business logic in `server.py`
- Side effects (e.g. notification stub in `finish.py`) are a no-op comment for now — wired later

### `server.py`
- `mcp = FastMCP("tasks_mcp")`
- Imports all tool modules (registration happens at import time via `@mcp.tool`)
- Entry point: `mcp.run(transport="streamable-http", port=8000)`

---

## TDD Order

Write the failing test first. Implement only enough to pass it. Move to the next.

### Stage 1 — Foundation

**`test_models.py`** → **`models.py`**
- Task creates with required fields, sets defaults correctly
- `created_at` / `updated_at` are UTC
- `due_date` accepts valid ISO date, rejects datetime strings
- Priority defaults to `medium`, status defaults to `active`

**`test_store.py`** → **`store.py`**
- `add` returns task with generated UUID
- `get_for_user` returns task when owner matches
- `get_for_user` raises `TaskNotFound` when task missing or wrong owner (same exception — no leaking)
- `list` filters by `user_id` only
- `update` writes changes and bumps `updated_at`

---

### Stage 2 — Tools (one file at a time, same pattern each)

For each tool file, the test covers:
1. Happy path — valid input, correct output shape
2. Default `user_id` — omitting `user_id` resolves to `"default"`
3. Input validation — Pydantic rejects bad inputs before the tool runs
4. Error cases — exact messages from the spec

**Order matches dependency: write tools → then test reads that depend on writes**

```
test_add.py       → add.py        happy path, empty title, bad due_date
test_finish.py    → finish.py     happy path, idempotent, already-cancelled error
test_cancel.py    → cancel.py     happy path, idempotent, already-complete error
test_defer.py     → defer.py      happy path, past date rejected, terminal task rejected
test_update.py    → update.py     happy path, no changes error, terminal task rejected
test_get.py       → get.py        found, not found, wrong owner = not found
test_list.py      → list.py       status filter, priority filter, due_before filter, pagination
test_focus.py     → focus.py      overdue + due-today returned, correct sort order, counts
test_search.py    → search.py     matches title, matches notes, case-insensitive, min length
```

---

### Stage 3 — E2E

**`test_server.py`** — connects to a live server instance

**Strategy:** FastMCP provides an in-process test client (`Client(mcp_instance)`) that speaks the full MCP protocol without a network hop. Tests in `test_e2e/` use this — no subprocess, no port binding needed for the test suite.

For manual / live validation before delivery, the server is started via:
```
uv run python -m tasks_mcp.server
```
Then tested with MCP Inspector:
```
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

**E2E test scenarios (one test per scenario):**
1. Full task lifecycle: add → finish → verify status
2. Full cancel lifecycle: add → cancel → verify status
3. Ownership isolation: add as `user_a` → get as `user_b` → not found
4. Default user: add without `user_id` → list without `user_id` → task appears
5. `tasks_focus` returns only overdue + today, sorted high→low
6. `tasks_search` finds by title and notes substring
7. `tasks_list` pagination: add 5 tasks, list with limit=2, verify `has_more` + `next_offset`
8. `tasks_defer` then `tasks_list` with `due_before` reflects new date
9. `tasks_update` then `tasks_get` reflects changes, `updated_at` > `created_at`
10. `tasks_finish` is idempotent: call twice, second call returns same completed task

---

## Delivery Gate

Before marking implementation done:

- [ ] All unit tests pass: `uv run pytest tests/unit`
- [ ] All e2e tests pass: `uv run pytest tests/e2e`
- [ ] Server starts cleanly: `uv run python -m tasks_mcp.server`
- [ ] MCP Inspector connects and lists all 9 tools
- [ ] Each tool is callable from MCP Inspector with valid inputs
- [ ] Each tool returns the correct error for at least one invalid input
- [ ] No secrets in code or config files
