# AI Agent Vision

This project consists of a backend service for receipt analysis using AI vision capabilities and a SvelteKit frontend for user interaction.

## Project Structure

- `backend/` - Python backend with FastAPI and AI agents
  - `agents/` - AI agent modules for receipt processing
  - `common/` - Shared utilities and data storage abstractions
  - `webapp/` - FastAPI web service implementation
- `frontend/` - SvelteKit frontend application

## Features

### Current Features

- Receipt image upload and processing
- AI-powered receipt analysis that extracts:
  - Receipt metadata (date, place, total)
  - Individual items with prices and quantities
  - Item categorization
  - Loyalty discount detection
- JSON response from backend with complete receipt data
- Frontend display of receipt analysis results:
  - Receipt summary table
  - Loyalty discount summary with total savings
  - Detailed items table with highlighting for discounted items
- Receipt history:
  - View all previously processed receipts
  - Detailed view of past receipts with all analysis data
  - Summary of savings from loyalty discounts

## Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Frontend

```bash
# From the frontend directory
cd frontend
npm run dev
```

## Development

- Backend API runs on http://localhost:8000
- Frontend development server runs on http://localhost:5173

The pre-commit configuration includes:

- Black for Python code formatting
- isort for Python import sorting
- flake8 for Python code quality checks
- Prettier for frontend code formatting
- General hooks for trailing whitespace, file endings, etc.
