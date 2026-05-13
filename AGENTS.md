# Tasks Management System — Constitution

## What We Are Building

A multi-agent task management system where users interact in plain language. A central **Tasks Manager Agent** understands intent, delegates to specialist agents or tools, and the result surfaces through a web UI. Every component — from agents to APIs to the UI — runs on Kubernetes from day one.

```
User
 └─► Tasks Manager Agent
        ├─► Appointment Booking Agent  →  Google Sheets
        └─► Tasks MCP Server
                └─► Notifications API

Auth: Better Auth  |  UI: Next.js  |  Infrastructure: Kubernetes
```

---

## How We Work

### Always Verify Before Acting

Before taking any action — writing code, calling a tool, making a handoff, deploying a change — stop and confirm you understand what you are about to do and why. This applies to agents and developers equally.

- State the intent explicitly before executing.
- If the action is irreversible (a deploy, a data write, a delete), double-check inputs and context first.
- After acting, verify the outcome matches the expectation. Do not assume success — observe it.
- When in doubt, ask. A moment of clarification costs far less than recovering from a wrong action.

### Test-Driven Development

We write the test before we write the code. Always.

- Define the expected behavior as a failing test first.
- Write only enough code to make that test pass.
- Refactor, keeping tests green.

No feature, agent tool, API route, or UI component is considered done until it has a test that describes what it should do. Tests are not an afterthought — they are the first act of development.

### Read the Docs Before You Code

Before implementing anything with an SDK, framework, or library, consult the official documentation. Use an agent skill or MCP tool to fetch the relevant docs — do not rely on training knowledge alone, as APIs evolve.

This applies to every layer: OpenAI Agents SDK, Python MCP SDK, FastAPI, Next.js, Better Auth, Kubernetes. When in doubt, look it up first, then implement.

### One Responsibility Per Component

Each agent, service, and module does one thing well. The Tasks Manager Agent orchestrates — it does not persist data. The MCP server exposes task operations — it does not know about the UI. The Notification service notifies — it does not decide what warrants a notification. Keep boundaries clean and resist the urge to shortcut across them.

### Small, Honest Commits

Commit one logical change at a time. The commit message should explain *why* the change was made, not describe what the diff already shows. If you cannot summarize a commit in one sentence, it is probably two commits.

### No Clever Code

Prefer clear over clever. Future contributors should be able to read the code and understand it without context. If you feel the need to write a long comment explaining how something works, the code itself is probably wrong.

---

## Kubernetes-First Mindset

Every decision is made through the lens of running on Kubernetes in production. This is not something we bolt on at the end.

### Design for the Cluster from Day One

- Every service is a container. Local development runs the same container images that go to the cluster.
- Services discover each other by name, not by hardcoded addresses. Configuration lives in Kubernetes Secrets and ConfigMaps, not in `.env` files committed to the repo.
- No service assumes it is the only instance. All services are stateless and horizontally scalable from the first line of code.

### Image Registry

All container images are published to **GitHub Container Registry (ghcr.io)**. The repository is public, so images are public by default. Image names follow the pattern:

```
ghcr.io/irfanmanzoor12/32n/<service-name>:latest
ghcr.io/irfanmanzoor12/32n/<service-name>:<git-sha>
```

Always tag with both `latest` and the full git SHA. Never deploy `latest` to production — use the SHA tag so deployments are reproducible and rollbacks are exact.

### Dockerfile Location

Every service owns its `Dockerfile` at the root of its directory:

```
tasks-mcp-server/Dockerfile
notifications-api/Dockerfile
tasks-manager-agent/Dockerfile
ui/Dockerfile
```

No Dockerfiles at the repo root. Each service builds independently — `docker build -t <image> tasks-mcp-server/` from the repo root.

### Deployment Manifests

All Kubernetes manifests and Helm charts live in `deployment/` at the repo root, organised by service:

```
deployment/
├── tasks-mcp-server/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── notifications-api/
│   ├── deployment.yaml
│   └── service.yaml
└── helm/
    └── tasks-system/      # umbrella chart for full-stack deploy
```

Never commit environment-specific values (cluster URLs, credentials) into `deployment/`. Those live in Kubernetes Secrets and environment-specific values files that are not checked in.

### Health and Observability are Not Optional

Every service exposes a liveness probe and a readiness probe before it is considered production-ready. If Kubernetes cannot tell whether your service is healthy, your service is not done.

Structured logging from day one. Every log line has enough context to trace a request across services without needing to SSH into a pod.

### Fail Gracefully

Services will go down. Requests will fail. Design for it. Agents should handle tool call failures without crashing. APIs should return meaningful error responses. The UI should degrade gracefully when a backend service is unreachable.

### Secrets Stay in the Cluster

Credentials, API keys, and tokens live in Kubernetes Secrets — never in source code, never in container images, never in plain config files. If a secret can be read by checking out the repo, it is not a secret.

---

## Agent Principles

### Agents Orchestrate, Tools Act

Agents reason and route. MCP tools and APIs perform the actual work. An agent that reaches into a database directly is doing too much. Keep agents thin and tools purposeful.

### Trust Flows Downward

The Tasks Manager Agent validates the user's identity and intent. Every downstream agent and tool trusts that the caller has already authenticated the user — but still enforces ownership. A task belonging to one user must never be visible or mutable by another.

### Handoffs are Explicit

When the Tasks Manager Agent delegates to the Appointment Booking Agent, it passes everything the sub-agent needs. Sub-agents do not reach back up the chain or make assumptions about global state.

---

## Development Principles

### Official Docs Are the Source of Truth

When building a feature that uses any SDK or framework, use an agent skill or MCP tool to retrieve the current official documentation. Implement based on that, not on memory or examples from a previous project.

### Every Service is Independently Deployable

A change to the Notifications API should not require redeploying the MCP server. A change to the UI should not require touching an agent. Design services so they can be updated, scaled, and rolled back independently.

### Migrate Forward, Never Backward

Database and sheet schema changes are additive. Do not delete or rename fields in a way that breaks existing data. Write migration steps that can be applied without downtime.

### Review at the Boundary

The only place we validate, sanitize, and enforce rules is at the boundary where untrusted input enters the system — the UI form, the agent's user message, the API's incoming request. Everywhere else, trust internal contracts and move fast.

---

## Extensibility & Multi-Agent Team Patterns

These principles come from established best practices for building extensible, team-scale agent systems (Chapter 14-C: Extensibility & Teams).

### Design for Hooks, Not Polling

Automation should be event-driven. Agents and services react to events — a task created, a file changed, a commit pushed — rather than repeatedly checking for state changes. Polling is a smell. If something needs to happen when an event occurs, wire it to the event.

### Build Skills as Composable Plugins

Capabilities should be packaged as discrete, reusable skill modules — not baked into a single monolithic agent. Each skill does one thing, is independently testable, and can be shared across agents or teams. Skills load from a designated location and are discovered at runtime, not hardcoded at build time.

### Subagent Delegation is the Unit of Scale

When a task exceeds a single agent's scope, delegate to a specialist subagent — do not stretch the primary agent to cover everything. Subagents are invoked explicitly with everything they need; they do not assume global context. This is how the system scales to handle complexity without any single agent becoming a god object.

### Isolate Parallel Work with Worktrees

When multiple agents or developers work on the same system simultaneously, they must operate in isolated contexts. Use worktrees (or equivalent isolation) so concurrent tasks cannot interfere with each other. Isolation is not overhead — it is the difference between predictable parallelism and subtle corruption.

### Agents Must Be Operable Without a Human Present

Design every agent to run headlessly. An agent that can only function with a human watching and confirming each step is not production-ready. Remote and scheduled execution must be a first-class concern, not an afterthought. Agents should be able to complete their work, report results, and surface errors without requiring real-time supervision.

### Scheduled and Recurring Automation is a First-Class Pattern

Time-based triggers — reminders, recurring tasks, scheduled reports — are a core part of this system, not edge cases. Use cron-style scheduling as a built-in design primitive. Any task that needs to repeat or fire at a specific time should be modeled as a scheduled job from the start.

### React to Events Asynchronously

Agents should listen on event channels and respond when relevant events arrive, decoupled from the producer of that event. The MCP server does not wait for the Notifications API to confirm delivery before returning. The Tasks Manager Agent does not block waiting for the Appointment Booking Agent. Design for async handoffs and let each component move at its own pace.

### Core Patterns Must Be Platform-Agnostic

The fundamental patterns — event-driven hooks, plugin skills, subagent delegation, worktree isolation, scheduled automation — do not belong to any specific tool or runtime. Implement them in a way that could survive a change of underlying platform. Avoid tight coupling to any single SDK's quirks.

### Share and Document What You Build

Skills, hooks, and agent configurations built for this project should be documented well enough that another developer can pick them up without asking the author. When a pattern proves useful, extract it, name it clearly, and make it reusable. Good work compounds when it is shareable.

---

## Quality Gates

A piece of work is only done when:

1. A test was written first and it describes the expected behavior clearly.
2. The implementation makes that test pass without breaking existing tests.
3. The intent was stated before acting, and the outcome was verified after.
4. The service runs correctly in a container and its health probes respond.
5. The agent or service can run headlessly without human supervision.
6. No credentials or secrets exist anywhere in the code or config files.
7. The code can be read and understood without needing the author to explain it.
8. Any reusable skill or pattern is documented well enough for another developer to use it without asking.
