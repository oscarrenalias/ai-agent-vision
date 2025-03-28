#!/bin/bash

# Install backend dependencies
if [ -f "/workspaces/ai-agent-vision/backend/requirements.txt" ]; then
  echo "Installing backend dependencies..."
  pip install -r /workspaces/ai-agent-vision/backend/requirements.txt
fi

# Install frontend dependencies
if [ -d "/workspaces/ai-agent-vision/frontend" ]; then
  echo "Installing frontend dependencies..."
  cd /workspaces/ai-agent-vision/frontend
  npm install
fi

# Configure PostgreSQL
echo "Waiting for PostgreSQL to start..."
until pg_isready -h localhost -U postgres; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Create database schema if needed
echo "Setting up database..."
cd /workspaces/ai-agent-vision/backend
if [ -f "alembic.ini" ]; then
  alembic upgrade head
fi

# Configure Amazon Q if AWS credentials exist
if [ -f "/home/vscode/.aws/credentials" ]; then
  echo "AWS credentials found, configuring Amazon Q..."
  q configure
fi

echo "Development environment setup complete!"
