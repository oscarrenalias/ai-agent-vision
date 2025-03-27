# AI Agent Vision

This project consists of a backend service for receipt analysis using AI vision capabilities and a SvelteKit frontend for user interaction.

## Project Structure

- `backend/` - Python backend with FastAPI and AI agents
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

## Potential Future Features

- Sorting functionality for the items table (by price, category, etc.)
- Filtering options to show only items with discounts
- Charts and visualizations of spending by category
- Receipt comparison tool to compare prices across different stores
- Export functionality (PDF, CSV)
- User authentication and personal receipt storage
- Mobile-optimized interface with camera integration
- OCR pre-processing to improve receipt image quality
- Provide suggestions on recipes that could be prepared with the contents of the receipt
- Barcode scanning for quick product identification
- Integration with budgeting tools or expense trackers
