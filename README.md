# Tasks Management System

An AI-powered task and appointment manager that understands plain English. Tell it what you need — it handles the rest.

> **"add 8 pm reminder for friends meetup"** → task created, appointment booked, notification sent.

---

## What It Does

- Accepts natural-language task requests from users
- Automatically distinguishes between simple tasks and bookings
- Books appointments and records them in Google Sheets
- Sends notifications when tasks are created, updated, or deleted
- Runs entirely on Kubernetes — built for production from day one

---

## Architecture

```
User
 └─► Tasks Manager Agent         (OpenAI Agents SDK)
        ├─► Appointment Booking Agent  →  Google Sheets
        └─► Tasks MCP Server           (Python MCP SDK)
                └─► Notifications API  (FastAPI)

Auth:  Better Auth
UI:    Next.js
Infra: Kubernetes
```

### Components

| Component | Role | Technology |
|---|---|---|
| Tasks Manager Agent | Primary agent — understands user intent and routes requests | OpenAI Agents SDK |
| Appointment Booking Agent | Captures booking details, writes to Google Sheets | OpenAI Agents SDK |
| Tasks MCP Server | Exposes add / update / delete task tools | Python MCP SDK |
| Notifications API | Dispatches notifications on task events | FastAPI |
| Frontend | User interface with streaming agent responses | Next.js |
| Auth | Session management and login | Better Auth |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Kubernetes cluster (local: [minikube](https://minikube.sigs.k8s.io/) or [kind](https://kind.sigs.k8s.io/))
- An OpenAI API key
- A Google Cloud service account with Sheets access

### Local Setup

```bash
# Clone the repo
git clone https://github.com/irfanmanzoor12/32N.git
cd 32N

# Python services
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ui && npm install

# Environment
cp .env.example .env
# Fill in your keys in .env
```

### Running Locally

```bash
# MCP Server
python -m tasks_mcp

# Notifications API
uvicorn notifications.main:app --reload

# Frontend
cd ui && npm run dev
```

### Running on Kubernetes

Every service ships as a container. Kubernetes manifests live in `k8s/`.

```bash
kubectl apply -f k8s/
```

Secrets and config are managed via Kubernetes Secrets and ConfigMaps — never committed to the repo.

---

## Development

This project follows a strict set of working principles defined in [AGENTS.md](./AGENTS.md). Key highlights:

- **Test-Driven Development** — tests are written before code, always
- **Verify before acting** — state intent, then confirm the outcome
- **K8s-native** — every service is stateless, containerized, and horizontally scalable
- **Doc-first** — official SDK/framework docs are consulted before any implementation
- **Event-driven** — components communicate via events, not polling

### Running Tests

```bash
# Python
pytest

# JavaScript
npm test
```

---

## Project Principles

See [AGENTS.md](./AGENTS.md) for the full development constitution — covering agent design principles, Kubernetes-first thinking, extensibility patterns, and quality gates.

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
