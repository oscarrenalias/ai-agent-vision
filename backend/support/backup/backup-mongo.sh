#!/bin/bash
set -e

BACKUP_DIR="/backup/$(date +%F_%H-%M-%S)"
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"

mkdir -p "$BACKUP_DIR"
echo "[backup-mongo] Starting backup to $BACKUP_DIR"
mongodump --host "$MONGO_HOST" --port "$MONGO_PORT" --out "$BACKUP_DIR"
echo "[backup-mongo] Backup completed at $(date)"
