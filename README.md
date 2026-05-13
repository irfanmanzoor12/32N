# Tasks Management System

An AI-powered task and appointment manager that understands plain English. Tell it what you need — it handles the rest.

> **"add 8 pm reminder for friends meetup"** → task created, appointment booked, notification sent.

---

## Architecture

```
User
 └─► Tasks Manager Agent         (OpenAI Agents SDK)
        ├─► Appointment Booking Agent  →  Google Sheets
        └─► Tasks MCP Server           (Python + FastMCP)
                └─► Notifications API  (FastAPI)

Auth:  Better Auth
UI:    Next.js
Infra: Kubernetes
```

### Components

| Component | Role | Technology | Status |
|---|---|---|---|
| Tasks MCP Server | Exposes 9 intent-based task tools over MCP | Python + FastMCP | ✅ Built |
| Tasks Manager Agent | Primary agent — understands user intent and routes requests | OpenAI Agents SDK | Planned |
| Appointment Booking Agent | Captures booking details, writes to Google Sheets | OpenAI Agents SDK | Planned |
| Notifications API | Dispatches notifications on task events | FastAPI | Planned |
| Frontend | User interface with streaming agent responses | Next.js | Planned |
| Auth | Session management and login | Better Auth | Planned |

---

## Repository Structure

```
32r/
├── tasks-mcp-server/      # MCP server — 9 intent-based task tools (built)
│   ├── src/tasks_mcp/
│   │   ├── server.py      # FastMCP entry point, registers all tools
│   │   ├── models.py      # Task Pydantic model, Priority/Status enums
│   │   ├── store.py       # In-memory TaskStore with ownership enforcement
│   │   └── tools/         # One file per tool (add, finish, cancel, defer,
│   │                      #   update, get, list, focus, search)
│   └── tests/             # Unit + e2e tests (pytest + pytest-asyncio)
├── specs/
│   └── mcp-server/        # Decisions, implementation plan, tool specs
└── AGENTS.md              # Development constitution
```

---

## Tasks MCP Server

### Tools

| Tool | Intent |
|---|---|
| `tasks_add` | Create a task |
| `tasks_finish` | Mark a task complete |
| `tasks_cancel` | Abandon a task |
| `tasks_defer` | Reschedule a task |
| `tasks_update` | Edit task fields |
| `tasks_get` | Look up one task |
| `tasks_list` | Browse tasks with filters |
| `tasks_focus` | What should I work on now? |
| `tasks_search` | Find tasks by content |

### Running

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
cd tasks-mcp-server
uv run python -m tasks_mcp.server
# Listening on http://127.0.0.1:8000/mcp
```

### Testing

```bash
cd tasks-mcp-server

# Unit tests
uv run pytest tests/unit

# E2E tests
uv run pytest tests/e2e

# All tests
uv run pytest
```

### Connecting to Claude Code

Add `.mcp.json` to the project root:

```json
{
  "mcpServers": {
    "tasks": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Or via CLI:

```bash
claude mcp add --transport http tasks http://localhost:8000/mcp --scope project
```

### Inspecting with MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

---

## Development Principles

Defined in [AGENTS.md](./AGENTS.md). Key highlights:

- **Test-Driven** — tests are written before code, always
- **Verify before acting** — state intent, confirm the outcome
- **K8s-native** — every service is stateless, containerized, horizontally scalable
- **Doc-first** — official SDK/framework docs consulted before any implementation
- **Event-driven** — components communicate via events, not polling

---

## Contributing

1. Branch from `main`: `feat/<description>` or `fix/<description>`
2. Write the test first
3. Make it pass
4. Open a PR — one logical change per PR

Do not commit `.env` files, secrets, or service account credentials.

---

## License

MIT
