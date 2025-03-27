from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from agents.orchestrator import Orchestrator
import logging

class ReceiptResponse(BaseModel):
    status: Literal["success", "failed"]
    error: Optional[str] = None

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

#
# can be removed later, for now this is useful to trigger the opeartion with a simple GET
#
@app.get("/test")
async def test() -> ReceiptResponse: 
    orchestrator = Orchestrator()
    result = orchestrator.run(receipt_image_path="data/samples/receipt_sample_1_small.jpg")        
    logging.info(f"Receipt processing result: {result}")
    return ReceiptResponse(
        status="success"
    )

@app.post("/process", response_model=ReceiptResponse)
async def process_receipt(file: UploadFile = File(...)) -> ReceiptResponse:
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
            
        orchestrator = Orchestrator()
        result = orchestrator.run(receipt_image_path="data/samples/receipt_sample_1_small.jpg")        

        logging.info(f"Receipt processing result: {result}")
        
        return ReceiptResponse(
            status="success"
        )
        
    except Exception as e:
        return ReceiptResponse(
            status="failed",
            error=str(e)
        )