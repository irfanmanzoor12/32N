# MCP Server — Decisions

## Settled

| Decision | Choice | Reason |
|---|---|---|
| Transport | Stateless Streamable HTTP | Multi-agent, deployed, horizontally scalable on K8s |
| Auth | None (for now) | Simplest version first |
| Language | Python + FastMCP | uv is the package manager; Python aligns with the rest of the stack |
| Deployment | Kubernetes Deployment (stateless) | K8s-first, matches stateless transport |
| Session model | Stateless | No session persistence between requests |
| Storage | In-memory Map | No database for now; shape is DB-ready |
| Tool design | Intent-based (9 tools) | Maps to human work intent, not CRUD operations |
| Notifications | Internal side effect in tools | Agents don't orchestrate notifications directly |

---

## Open

- [x] Trust model between agents and MCP server — resolved: caller passes `user_id` in every tool call; the MCP server enforces ownership per tool (same `TaskNotFound` error for missing or wrong-owner tasks — no leaking). No network-level auth yet; deferred to auth phase below.

---

## TBD / Deferred

- Auth strategy (OAuth 2.1 vs API keys) — deferred until needed
- Per-agent tool scoping
- Multi-environment K8s config (dev/staging/prod)
