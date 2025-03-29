import logging
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Path, UploadFile
from pydantic import BaseModel

from agents.orchestrator import Orchestrator
from common.datastore import get_data_store

from .receipt_repository import ReceiptRepository

# Create a module-specific logger
logger = logging.getLogger("webapp")

# Add a startup log message to verify logging is working
logger.info("Webapp module initialized")

load_dotenv()


class ReceiptResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None


class ReceiptListResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None
    receipts: List[Dict[str, Any]] = []


app = FastAPI()
data_store = get_data_store()  # Use the factory function to get the default data store (PostgreSQL)
receipt_repository = ReceiptRepository(data_store=data_store)


@app.post("/process", response_model=ReceiptResponse)
async def process_receipt(file: UploadFile = File(...)) -> ReceiptResponse:
    try:
        logger.info(f"Processing receipt file: {file.filename}")

        if not file.content_type.startswith("image/"):
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(400, "File must be an image")

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"receipt_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File saved to {file_path}")

        # Process the receipt using the saved file path
        orchestrator = Orchestrator()
        logger.info("Starting receipt analysis with orchestrator")
        result = orchestrator.run(receipt_image_path=file_path)

        logger.info(f"Receipt processing complete: {result}")

        # Extract receipt data from the result
        receipt_data = None
        receipt_data = result["receipt"]

        return ReceiptResponse(status="success", receipt=receipt_data)

    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}", exc_info=True)
        return ReceiptResponse(status="failed", error=str(e))


@app.get("/receipts", response_model=ReceiptListResponse)
async def get_all_receipts() -> ReceiptListResponse:
    """
    Retrieve all receipts from the database
    """
    try:
        receipts = receipt_repository.get_all_receipts()
        return ReceiptListResponse(status="success", receipts=receipts)
    except Exception as e:
        logger.error(f"Error retrieving receipts: {str(e)}", exc_info=True)
        return ReceiptListResponse(status="failed", error=str(e))


@app.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt_by_id(receipt_id: int = Path(..., title="The ID of the receipt to retrieve")) -> ReceiptResponse:
    """
    Retrieve a specific receipt by ID
    """
    try:
        logger.info(f"Retrieving receipt with ID: {receipt_id}")
        receipt = receipt_repository.get_receipt_by_id(receipt_id)
        if receipt:
            return ReceiptResponse(status="success", receipt=receipt)
        else:
            return ReceiptResponse(status="failed", error=f"Receipt with ID {receipt_id} not found")
    except Exception as e:
        logger.error(f"Error retrieving receipt {receipt_id}: {str(e)}", exc_info=True)
        return ReceiptResponse(status="failed", error=str(e))
