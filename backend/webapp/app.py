from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from agents.orchestrator import Orchestrator
from agents.receiptstate import Receipt
import logging
import os
import shutil
from datetime import datetime

class ReceiptResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None

app = FastAPI()

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
        #if result and hasattr(result, 'receipt') and result.receipt:
        #    # Convert the receipt object to a dict for JSON serialization
        #    receipt_data = result.receipt.dict() if hasattr(result.receipt, 'dict') else result.receipt
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