import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import chat, price_comparison, receipts

# --- Logging configuration moved from webapp.py ---
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s | %(levelname)-8s | access: %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "webapp": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "agents": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "common": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(logging_config)
# --- End logging configuration ---

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

# Path to the SvelteKit build output (now inside backend/frontend/build)
frontend_build_path = os.path.join(os.path.dirname(__file__), "../frontend/build")

# Include routers (API endpoints) with /api prefix
app.include_router(chat.router)
app.include_router(receipts.router)
app.include_router(price_comparison.router)

# Serve static files (must be last)
app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="static")


@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information
    """
    return {
        "name": "AI Agent Vision API",
        "version": "1.0.0",
        "description": "Backend API for receipt analysis with AI vision capabilities",
        "endpoints": {
            "receipts": "/api/receipts",
            "process": "/api/process",
            "chat": "/api/chat/send",
            "price_comparison": "/api/price-comparison",
        },
    }
