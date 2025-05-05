import logging
import os
import uuid

from fastapi import APIRouter, File, UploadFile

upload_router = APIRouter()

# Configure logging
logger = logging


@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # TODO: parameterize this part
        uploads_dir = os.path.join(os.path.dirname(__file__), "../../../uploads")

        os.makedirs(uploads_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1]
        file_id = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(uploads_dir, file_id)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File uploaded: {file_path}")
        return {"status": "success", "filename": file_id}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return {"status": "error", "error": str(e)}
