# Notifications API — Decisions

## Settled

| Decision | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Python aligns with the stack; async-capable; auto-generates OpenAPI docs |
| Transport | HTTP REST (port 8001) | Simple request/response; no streaming needed for v1 |
| Language | Python + uv | Consistent with tasks-mcp-server |
| Deployment | Kubernetes Deployment (stateless) | K8s-first; no session state needed |
| Channel dispatch | Pluggable (`BaseDispatcher` ABC) | Log-only now; real channels (email, push) wired later without changing the API |
| Event model | Enum-validated `EventType` | Unknown events rejected at the boundary with 422 |
| Health probes | `/health/live` + `/health/ready` | Required by K8s liveness/readiness checks |
| Response code | 202 Accepted | Dispatch is fire-and-forget; caller doesn't wait for delivery confirmation |

---

## Open

- [ ] Auth — how does the MCP server authenticate when calling `/notify`?

---

## TBD / Deferred

- Real channel implementations (email via SMTP/SendGrid, push via FCM)
- Retry logic for failed dispatches
- Notification history / audit log
- Per-user notification preferences
