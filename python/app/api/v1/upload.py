"""
File Upload API endpoints
Handles photo uploads for quality verification and other features
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Configure upload directory — use /tmp on App Engine/Cloud Run (read-only filesystem)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads/quality_photos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image", response_model=Dict[str, str])
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for quality verification
    
    Returns the URL of the uploaded image
    """
    try:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}{file_ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Generate URL (in production, this would be an S3 URL or CDN URL)
        # For now, return a relative path
        photo_url = f"/uploads/quality_photos/{filename}"
        
        logger.info(f"Image uploaded successfully: {filename}")
        
        return {
            "success": True,
            "url": photo_url,
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload photo: {str(e)}"
        )


@router.post("/document", response_model=Dict[str, str])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document
    """
    # For now, reuse photo logic but with different allowed extensions
    return await upload_image(file)


@router.delete("/photo/{filename}", response_model=Dict[str, str])
async def delete_photo(filename: str):
    """
    Delete an uploaded photo
    """
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )
        
        os.remove(filepath)
        
        logger.info(f"Photo deleted successfully: {filename}")
        
        return {
            "success": True,
            "message": "Photo deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting photo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete photo: {str(e)}"
        )
