FROM ubuntu:22.04

# Install cron, wget, gnupg, and ca-certificates
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron wget gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add MongoDB repo and install database tools (mongodump, etc.)
RUN wget -qO - https://pgp.mongodb.com/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" > /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends mongodb-database-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy backup script and crontab
COPY backup-mongo.sh /usr/local/bin/backup-mongo.sh
COPY backup-cron /etc/cron.d/backup-cron

RUN chmod +x /usr/local/bin/backup-mongo.sh \
    && chmod 0644 /etc/cron.d/backup-cron \
    && crontab /etc/cron.d/backup-cron

# Create backup directory (will be mounted as a volume)
RUN mkdir -p /backup

# Run cron in foreground
CMD ["cron", "-f"]
