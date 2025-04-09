import logging
import os
import shutil
import threading
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, File, HTTPException, Path, UploadFile
from pydantic import BaseModel

from agents.orchestrator import Orchestrator
from common.datastore import get_data_store
from common.job_store import JobStatus, JobStore
from webapp.receipt_repository import ReceiptRepository

# Create a module-specific logger
logger = logging.getLogger("webapp.routers.receipts")


class ReceiptResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None


class ReceiptListResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None
    receipts: List[Dict[str, Any]] = []


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Create a router for receipt endpoints
router = APIRouter(prefix="/api", tags=["receipts"])

data_store = get_data_store()  # Use the factory function to get the default data store (MongoDB)
receipt_repository = ReceiptRepository(data_store=data_store)
job_store = JobStore()


def process_receipt_task(file_path: str, job_id: str):
    """Background task to process a receipt image"""
    try:
        # Update job status to processing
        job_store.update_job_status(job_id, JobStatus.PROCESSING)

        # Process the receipt using the saved file path
        orchestrator = Orchestrator()
        logger.info(f"Starting receipt analysis with orchestrator for job {job_id}")
        result = orchestrator.run(receipt_image_path=file_path)

        logger.info(f"Receipt processing complete for job {job_id}")

        # Extract receipt data from the result
        receipt_data = result["receipt"]

        # Update job status to completed with the result
        job_store.update_job_status(job_id, JobStatus.COMPLETED, result=receipt_data)

    except Exception as e:
        logger.error(f"Error processing receipt for job {job_id}: {str(e)}", exc_info=True)
        job_store.update_job_status(job_id, JobStatus.FAILED, error=str(e))


@router.post("/process", response_model=JobResponse)
async def process_receipt(file: UploadFile = File(...)) -> JobResponse:
    try:
        logger.info(f"Received receipt file: {file.filename}")

        if not file.content_type.startswith("image/"):
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(400, "File must be an image")

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
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

        # Create a new job in the job store
        job_id = job_store.create_job(file_path)

        # Start processing in a separate thread to avoid blocking FastAPI's event loop
        thread = threading.Thread(target=process_receipt_task, args=(file_path, job_id))
        thread.daemon = True
        thread.start()

        return JobResponse(job_id=job_id, status="accepted", message="Receipt processing started")

    except Exception as e:
        logger.error(f"Error initiating receipt processing: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Error processing receipt: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get the status of a receipt processing job"""
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(404, f"Job with ID {job_id} not found")

    return JobStatusResponse(job_id=job["job_id"], status=job["status"], result=job["result"], error=job["error"])


@router.get("/receipts", response_model=ReceiptListResponse)
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


@router.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt_by_id(receipt_id: str = Path(..., title="The ID of the receipt to retrieve")) -> ReceiptResponse:
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
