FROM mcr.microsoft.com/devcontainers/python:3.10

# Install PostgreSQL client tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN pip install --upgrade pip \
    && pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pytest

# Install Node.js and npm for frontend development
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Install global npm packages
RUN npm install -g svelte-check

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Install Amazon Q CLI
RUN pip install amazon-q-cli

# Ensure Amazon Q is in PATH
RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> /etc/bash.bashrc

# Create a non-root user to use if preferred
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Set the default shell to bash rather than sh
ENV SHELL /bin/bash

# Add a .bashrc entry to ensure Amazon Q is available for the vscode user
RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> /home/vscode/.bashrc
