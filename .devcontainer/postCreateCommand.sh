#!/bin/bash

## Disabling for now as it speeds up the process to provision the Codespace
# Install backend dependencies
#if [ -f "/workspaces/ai-agent-vision/backend/requirements.txt" ]; then
#  echo "Installing backend dependencies..."
#  pip install -r /workspaces/ai-agent-vision/backend/requirements.txt
#fi

# Install development dependencies including pre-commit
if [ -f "/workspaces/ai-agent-vision/backend/requirements-dev.txt" ]; then
  echo "Installing development dependencies..."
  pip install -r /workspaces/ai-agent-vision/backend/requirements-dev.txt
  echo "Setting up pre-commit hooks..."
  cd /workspaces/ai-agent-vision
  pre-commit install
fi

## Disabling for now as it speeds up the process to provisio the Codespace
# Install frontend dependencies
#if [ -d "/workspaces/ai-agent-vision/frontend" ]; then
#  echo "Installing frontend dependencies..."
#  cd /workspaces/ai-agent-vision/frontend
#  npm install
#fi

# Configure MongoDB
echo "Waiting for MongoDB to start..."
until mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  echo "Waiting for MongoDB to be ready..."
  sleep 2
done
echo "MongoDB is ready!"

# Create initial database setup if needed
echo "Setting up MongoDB database..."
mongosh --eval "use receipts"

# Configure Amazon Q if AWS credentials exist
if [ -f "/home/vscode/.aws/credentials" ]; then
  echo "AWS credentials found, configuring Amazon Q..."
  q configure
fi

echo "Development environment setup complete!"
