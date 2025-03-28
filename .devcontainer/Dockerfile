FROM mcr.microsoft.com/devcontainers/python:3.13

# Install PostgreSQL client tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set up Python environment
#RUN pip install --upgrade pip \
#    && pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pytest

# Install AWS Q CLI
RUN curl "https://desktop-release.codewhisperer.us-east-1.amazonaws.com/latest/q-x86_64-linux-musl.zip" -o "amazon-q-cli.zip" \
    && unzip amazon-q-cli.zip \
    && mv q/bin/* /usr/local/bin \
    && rm -rf amazon-q-cli.zip

# Ensure Amazon Q is in PATH
RUN echo 'export PATH="$PATH:$HOME/bin"' >> /etc/bash.bashrc

# Create a non-root user to use if preferred
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Set the default shell to bash rather than sh
ENV SHELL /bin/bash

# Add a .bashrc entry to ensure Amazon Q is available for the vscode user
RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> /home/vscode/.bashrc
