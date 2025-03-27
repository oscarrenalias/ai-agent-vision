# AI Agent Vision

This project consists of a backend service for receipt analysis using AI vision capabilities and a SvelteKit frontend for user interaction.

## Project Structure

- `backend/` - Python backend with FastAPI and AI agents
- `frontend/` - SvelteKit frontend application

## Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the required libraries
pip install -r requirements.txt
```

## Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Configuration

The following environment variables will be required:

* HUGGINGFACEHUB_API_TOKEN

## Running the application

### Backend

```bash
# From the backend directory
cd backend
python main.py  # Run the AI processing directly
# OR
python webapp.py  # Run the FastAPI web service
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