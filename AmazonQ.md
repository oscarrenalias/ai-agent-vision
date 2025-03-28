# Amazon Q Integration

This document describes the integration of Amazon Q into the AI Agent Vision project.

## Changelog

### March 28, 2025

- Added devcontainer configuration with:
  - Python 3.10 environment
  - PostgreSQL 15 database that starts automatically
  - Node.js for frontend development
  - Amazon Q CLI integration
  - AWS CLI v2
  - VS Code extensions for development
  - Automatic setup of development environment

### Features Added

- **Dockerfile** with:
  - Python 3.10 as the base
  - PostgreSQL client tools
  - Node.js and npm for frontend development
  - AWS CLI v2
  - Amazon Q CLI
  - PATH configuration to ensure Amazon Q is available

- **docker-compose.yml** that:
  - Sets up the application container
  - Configures a PostgreSQL 15 database
  - Mounts AWS credentials for Amazon Q
  - Ensures PostgreSQL starts automatically with health checks

- **devcontainer.json** with:
  - VS Code extensions for Python, Svelte, PostgreSQL, and AWS development
  - Proper formatter settings for different file types
  - PATH configuration for Amazon Q in the terminal
  - Port forwarding for frontend (5173), backend (8000), and PostgreSQL (5432)

- **postCreateCommand.sh** script that:
  - Installs backend and frontend dependencies
  - Waits for PostgreSQL to start
  - Sets up the database schema using Alembic if available
  - Configures Amazon Q if AWS credentials are found

## Usage

To use this setup:
1. Commit these files to your repository
2. Reopen your project in a new Codespace or rebuild the current one
3. The container will build with all dependencies and PostgreSQL will start automatically

You can then access your PostgreSQL database at localhost:5432 with the credentials:
- Username: postgres
- Password: postgres
- Database: receipts

And Amazon Q will be available by simply typing `q` in the terminal.
