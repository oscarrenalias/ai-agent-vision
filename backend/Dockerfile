# syntax=docker/dockerfile:1

# --- Build stage ---
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libxml2-dev libxslt1-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Final stage ---
FROM python:3.13-slim AS final
WORKDIR /app
COPY --from=build /install /usr/local
COPY . .
EXPOSE 8000
CMD ["python", "server.py"]
