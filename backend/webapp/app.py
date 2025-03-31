import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chat, receipts

# Create a module-specific logger
logger = logging.getLogger("webapp")

# Add a startup log message to verify logging is working
logger.info("Webapp module initialized")

load_dotenv()

app = FastAPI(title="AI Agent Vision API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(receipts.router)


@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information
    """
    return {
        "name": "AI Agent Vision API",
        "version": "1.0.0",
        "description": "Backend API for receipt analysis with AI vision capabilities",
        "endpoints": {"receipts": "/api/receipts", "process": "/api/process", "chat": "/api/chat/send"},
    }
