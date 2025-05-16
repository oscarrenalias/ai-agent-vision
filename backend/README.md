# 🚧 Preparations for local development 🚧

## 🧱 DevContainer

The preferred way to run the application to use the DevContainer in VSCode, which is preconfigured with the right components and dependencies.

Pre-requisites:

- Visual Studio Code
- A Docker runtime – Docker CLI from brew and Podman Desktop work well together on MacOS

The following instructions assume that they're being executed inside the DevContainer.

## 💻 Virtual environment and dependencies

Initialy virtual environment and install dependencies:

```bash
# Create and load virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

## 💻 Configure the application for local development

Copy `.env.example` file to `.env` and update values accordingly:

```bash
# Copy template
cp .env.example .env

# Edit the file and customize values
```

## ⚙️ Running the application

Run the application:

```bash
python server.py
```

Application will be available at http://localhost:8000.

## 🔎 Pre-Commit hooks

This project uses pre-commit hooks to ensure code quality and consistent formatting:

```bash
# Install the git hooks
pre-commit install

# Run the hooks on all files (optional)
pre-commit run --all-files
```

The pre-commit configuration includes:

- Black for Python code formatting
- isort for Python import sorting
- flake8 for Python code quality checks
- Prettier for frontend code formatting
- General hooks for trailing whitespace, file endings, etc.

## 🔎 Unit tests

Run with pytest from the backend folder:

```
pytest -v
```

⚠️ Please note that tests do not work yet.
