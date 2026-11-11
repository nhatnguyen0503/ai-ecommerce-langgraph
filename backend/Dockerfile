# syntax=docker/dockerfile:1

#---------- Stage 1: build the virtualenv with uv ----------
FROM python:3.12-slim AS builder

# Copy the uv binary from its offical image (pinned version).
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 1) Dependencies first: this layer is cached until pyproject/uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Then the application code (changes often, so it comes last).
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# ---------- Stage 2: small runtime image ----------
FROM python:3.12-slim

# Run as a normal user, never as root.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

# Docker marks the container "unhealthy" if /health stops answering.
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# Apply DB migrations, then start the API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]