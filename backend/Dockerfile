# syntax=docker/dockerfile:1

# --- Build stage ---
FROM python:3.12-slim AS build
WORKDIR /app
COPY uv.lock ./
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libxml2-dev libxslt1-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv
RUN uv sync --system --no-cache-dir

# --- Final stage ---
FROM python:3.12-slim AS final
WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY . .
EXPOSE 8000
CMD ["python", "server.py"]
