# AI Agent Vision

AI Agent Vision is a full-stack AI-powered application for grocery management, receipt scanning, and recipe management. It consists of a Python backend using LangChain/LangGraph and a Next.js frontend with CopilotKit integration.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Prerequisites and Setup
```bash
# Install uv package manager (if not available)
pip3 install uv

# Install dependencies for both components
cd backend && uv sync && uv sync --group dev && uv sync --group cli
cd ../ui && npm install
```

### Bootstrap and Build Process
**NEVER CANCEL BUILDS OR LONG-RUNNING COMMANDS**

Backend (fast builds):
```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate
uv sync                    # Takes ~5 seconds
uv build                   # Takes ~1.3 seconds - NEVER CANCEL, set timeout to 60+ seconds
```

Frontend (longer builds):
```bash
cd ui
npm install                # Takes ~35 seconds - NEVER CANCEL, set timeout to 60+ minutes
npm run build             # Takes ~50 seconds - NEVER CANCEL, set timeout to 60+ minutes
```

### Testing and Quality Checks
Backend testing:
```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate
uv run pytest            # Takes ~5 seconds - NEVER CANCEL, set timeout to 30+ minutes
                         # Note: Some tests may fail due to network connectivity (expected in sandboxed environments)
```

Backend linting (all fast, < 1 second each):
```bash
cd backend
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
uv run flake8 . --count --statistics
uv run black --check .
uv run isort --check-only --profile black .
```

Frontend linting:
```bash
cd ui
npm run lint             # Takes ~3 seconds after initial ESLint setup
```

### Running the Application

Backend server:
```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"
source .venv/bin/activate
# Copy environment file (required)
cp .env.example .env
# Edit .env to set OPENAI_API_KEY and MongoDB connection
uv run python server.py  # Starts on http://localhost:8000
```

Frontend development server:
```bash
cd ui
npm run dev              # Starts on http://localhost:3000 in < 1 second
```

CLI interface:
```bash
cd backend
uv run python cli.py     # Text-based chatbot interface
```

### Pre-commit Hooks
```bash
cd backend
source .venv/bin/activate
pre-commit install       # Takes < 1 second
pre-commit run --all-files  # Optional validation
```

## Validation

### Manual Testing Requirements
**CRITICAL**: After making any changes, ALWAYS validate functionality by running complete user scenarios:

1. **Backend API Testing**: Start backend server and verify:
   - Server starts without errors on port 8000
   - MongoDB connection is established (check logs)
   - API endpoints respond correctly

2. **Frontend Integration Testing**: Start frontend and verify:
   - UI loads correctly on port 3000
   - CopilotKit integration works
   - File upload functionality works
   - Charts and analytics display properly

3. **End-to-End Workflow**: Test complete user flows:
   - Upload a receipt image
   - View analytics dashboards
   - Add/manage recipes
   - Chat with AI agent

### Database Requirements
- MongoDB is required for full functionality
- Use Docker for local development: `docker run -d -p 27017:27017 --name mongo-test mongo:7`
- Application expects MongoDB on `mongodb://localhost:27017`
- Database name: `receipts`

### Known Limitations and Workarounds
- Network-dependent tests (recipe retrieval) will fail in sandboxed environments - this is expected
- Change streams require MongoDB replica set - single instance will show warnings but works for development
- CLI requires `uv sync --group cli` for prompt_toolkit dependencies
- Frontend ESLint setup is interactive on first run - select "Strict (recommended)"

## Development Guidelines

### Technology Stack
- **Backend**: Python 3.12, uv dependency management, LangChain/LangGraph, FastAPI, MongoDB
- **Frontend**: Next.js 15, TypeScript, CopilotKit, Tailwind CSS, Material-UI
- **Database**: MongoDB with Motor async driver
- **AI**: OpenAI GPT-4o (requires API key)

### Code Standards
- Backend: Black formatting (line length 127), isort, flake8
- Frontend: ESLint strict configuration, TypeScript strict mode
- Always run linting before committing: `pre-commit run --all-files`

### LangChain & LangGraph Guidelines
- Use ChatPromptTemplate.invoke() with dict objects
- Do not use to_messages() or to_string()
- Leverage LangGraph for complex agent workflows

### File Structure and Key Components
```
backend/
├── agents/           # AI agent implementations
├── common/          # Shared utilities and database connections
├── server.py        # FastAPI server entry point
├── cli.py           # Command-line interface
└── pyproject.toml   # uv configuration

ui/
├── src/app/         # Next.js app router structure
├── components/      # React components including CopilotKit
├── api/            # API route handlers
└── package.json    # npm configuration
```

### Common Tasks Reference

**Add backend dependency**: `uv add package_name`
**Add frontend dependency**: `npm install package_name`
**Format backend code**: `uv run black . && uv run isort . --profile black`
**Check types**: Frontend uses TypeScript strict mode
**Environment variables**: Copy `.env.example` to `.env` in backend/

### CI/CD Notes
- GitHub Actions runs on Python 3.12
- Backend CI includes: lint, test, build steps
- Frontend build is part of release workflow
- Docker images are built and published to GitHub Container Registry
- Deployment targets Raspberry Pi 5 via .deb packages

## Timeout Values for Long-Running Commands
**CRITICAL**: Always use appropriate timeouts and NEVER cancel these commands:

- `npm install`: Set timeout to 60+ minutes
- `npm run build`: Set timeout to 60+ minutes  
- `uv build`: Set timeout to 60+ seconds (usually ~1.3s)
- `uv run pytest`: Set timeout to 30+ minutes (usually ~5s)
- Backend server startup: Usually immediate, but allow 60+ seconds for model initialization