# syntax=docker/dockerfile:1

# --- Build stage ---
FROM python:3.12-slim AS build
WORKDIR /app
COPY uv.lock ./
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libxml2-dev libxslt1-dev libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# --- Final stage ---
FROM python:3.12-slim AS final
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY . .

# Ensure uploads directory exists
RUN mkdir -p /app/uploads

# Sync the project and clean up cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked \
    && find /usr/local/lib/python3.12 -name __pycache__ -exec rm -rf {} +

EXPOSE 8000
CMD ["/app/.venv/bin/python", "server.py"]
