from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


class DocumentRequest(BaseModel):
    url: str


@router.post("/process")
async def process_document(request: DocumentRequest):  
    """
    Process a document (image or PDF) from URL using advanced OCR
    """
    try:
        logger.info(f"Processing document from URL: {request.url}")
        
        result = await ocr_service.process_document_from_url(request.url)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=422, 
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_document endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during OCR processing: {str(e)}"
        )