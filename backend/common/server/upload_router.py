import logging
import os
import uuid

from fastapi import APIRouter, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorClient

from common.server.utils import get_uploads_folder

upload_router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DATABASE", "receipts")
AGGREGATES_COLLECTION = "aggregates"

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]


@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    def make_response(success: bool, file_id: str = None, error: str = None):
        response = {}
        if success:
            response["status"] = "success"
            if file_id is None:
                raise ValueError("file_id cannot be None if success is True")
            response["id"] = file_id
            return response

        if error:
            response["status"] = "error"
            if error is None:
                raise ValueError("error cannot be None if success is False")
            response["error"] = error

            return response

    try:
        uploads_dir = get_uploads_folder()

        os.makedirs(uploads_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1]
        file_id = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(uploads_dir, file_id)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        response = make_response(success=True, file_id=file_id)
        logger.info(f"File uploaded: {file_path}, Response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return make_response(success=False, error=str(e))
