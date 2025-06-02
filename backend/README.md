# Backend

This is the Python backend for the application.

## 🧰 Pre-requisites

The following are required to run the application:

- Visual Studio Code
- A Docker runtime – in MacOS, `colima` works great: https://github.com/abiosoft/colima
- An OpenAI API key, required for making calls to the OpenAPI models. Please sign up at https://platform.openai.com and load some credit into your account (5-10€/$ recommended)

## 🧱 DevContainer

The preferred way to run the application to use the DevContainer in VSCode, which is preconfigured with the right components and dependencies.

The following instructions assume that they're being executed inside the DevContainer.

## 💻 Virtual environment and dependencies

Initiate virtual environment and install dependencies:

```bash
# Create and load virtual environment
uv venv
source .venv/bin/activate

# Install project dependencies and dev dependencies
uv sync
uv sync --group dev
```

This shoud be taken care by the DevContainer as part of the initialization.

## 💻 Configure the application for local development

Copy `.env.example` file to `.env` and update values accordingly:

```bash
# Copy template
cp .env.example .env

# Edit the file and customize values
```

## ⚙️ Running the application

Run the application in server mode:

```bash
uv run python server.py
```

Application will be available at http://localhost:8000.

The application can also be run as a text-based command line chatbot:

```bash
uv run python cli.py
```

Please note that some features do not work in chatbot mode, such as automatic udpates of analytics data when contents of Mongo database change

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
uv run pytest
```
