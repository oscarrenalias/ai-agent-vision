#!/bin/bash
set -e

# Source the .env file for MONGO_URI
if [ -f /app/.env ]; then
  echo "[backup-mongo] Sourcing environment variables from /app/.env"
  set -a
  source /app/.env
  set +a
else
  echo "[backup-mongo] Warning: /app/.env file not found."
  exit 1
fi

BACKUP_DIR="/backup/$(date +%F_%H-%M-%S)"

mkdir -p "$BACKUP_DIR"
echo "[backup-mongo] Starting backup to $BACKUP_DIR"
if [ -n "$MONGODB_URI" ]; then
    echo "[backup-mongo] Using MONGODB_URI: $MONGODB_URI"
    mongodump --uri "$MONGODB_URI" --out "$BACKUP_DIR"
else
    echo "[backup-mongo] Error: MONGODB_URI is not set in /app/.env"
    exit 1
fi
echo "[backup-mongo] Backup completed at $(date)"
