# syntax=docker/dockerfile:1

# ── Stage 1: builder ─────────────────────────────────────────
# Installs all dependencies. Nothing from this stage reaches prod.
FROM python:3.12-slim AS builder

WORKDIR /app

# Bring in uv — pinned for reproducible builds
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Layer 1: deps only — cached until lockfile changes
# README.md required by uv_build (referenced in pyproject.toml)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# Layer 2: source — cached until src/ changes
COPY src/ ./src/
RUN uv sync --frozen --no-dev


# ── Stage 2: runtime ─────────────────────────────────────────
# Minimal image — no uv, no build tools, no test code.
FROM python:3.12-slim AS runtime

WORKDIR /app

# Non-root user — containers should never run as root
RUN addgroup --system app && adduser --system --ingroup app app

# Copy only the installed venv and source from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src   /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # 0.0.0.0 accepts connections from outside the container
    MCP_HOST="0.0.0.0" \
    MCP_PORT="8000" \
    NOTIFICATIONS_API_URL="http://notifications-api:8001"

USER app

EXPOSE 8000

# TCP-level check — verifies the server is listening on 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=4)" \
  || exit 1

CMD ["python", "-m", "tasks_mcp.server"]
