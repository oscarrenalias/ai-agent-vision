from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any, List
from agents.orchestrator import Orchestrator
from agents.receiptstate import Receipt
import logging
import os
import shutil
from datetime import datetime
from .receipt_repository import ReceiptRepository
from common.datastore import get_data_store
from dotenv import load_dotenv

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
        if not file.content_type.startswith('image/'):
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
        
        # Process the receipt using the saved file path
        orchestrator = Orchestrator()
        result = orchestrator.run(receipt_image_path=file_path)        

        logging.info(f"Receipt processing result: {result}")
        
        # Extract receipt data from the result
        receipt_data = None
        receipt_data = result["receipt"]
        
        return ReceiptResponse(
            status="success",
            receipt=receipt_data
        )
        
    except Exception as e:
        logging.error(f"Error processing receipt: {str(e)}")
        return ReceiptResponse(
            status="failed",
            error=str(e)
        )
    
@app.get("/receipts", response_model=ReceiptListResponse)
async def get_all_receipts() -> ReceiptListResponse:
    """
    Retrieve all receipts from the database
    """
    try:
        receipts = receipt_repository.get_all_receipts()
        return ReceiptListResponse(
            status="success",
            receipts=receipts
        )
    except Exception as e:
        logging.error(f"Error retrieving receipts: {str(e)}")
        return ReceiptListResponse(
            status="failed",
            error=str(e)
        )

@app.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt_by_id(receipt_id: int = Path(..., title="The ID of the receipt to retrieve")) -> ReceiptResponse:
    """
    Retrieve a specific receipt by ID
    """
    try:
        receipt = receipt_repository.get_receipt_by_id(receipt_id)
        if receipt:
            return ReceiptResponse(
                status="success",
                receipt=receipt
            )
        else:
            return ReceiptResponse(
                status="failed",
                error=f"Receipt with ID {receipt_id} not found"
            )
    except Exception as e:
        logging.error(f"Error retrieving receipt {receipt_id}: {str(e)}")
        return ReceiptResponse(
            status="failed",
            error=str(e)
        )
