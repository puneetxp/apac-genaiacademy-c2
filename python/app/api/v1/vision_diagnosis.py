"""
Multimodal Vision Diagnosis API Endpoint

Accepts crop/plant image uploads and returns AI-powered disease diagnosis
using Gemini's multimodal (vision) capabilities.

Demonstrates: Multimodal AI for image understanding — Google Cloud Hackathon criterion.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any
import logging

from app.services.vision_diagnosis_service import vision_diagnosis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vision", tags=["Vision AI"])


@router.post("/diagnose", response_model=Dict[str, Any])
async def diagnose_crop_disease(
    image: UploadFile = File(..., description="Photo of the crop/leaf to diagnose"),
    crop_name: Optional[str] = Form(None, description="Name of the crop (e.g. Rice, Tomato)"),
    region: Optional[str] = Form(None, description="State or district for regional context")
):
    """
    Upload a photo of a crop leaf/fruit and get an AI-powered disease diagnosis.

    Uses **Gemini Vision (multimodal)** to analyze the image and return:
    - Disease identification with confidence score
    - Severity assessment
    - Treatment options (organic, chemical, cultural)
    - Prevention recommendations
    - Urgency level

    This endpoint demonstrates **Multimodal AI** capabilities using Google Cloud Vertex AI.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{image.content_type}'. Accepted: JPEG, PNG, WebP."
        )

    # Read image bytes
    image_bytes = await image.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large. Maximum size is 10MB.")

    if len(image_bytes) < 1000:  # Suspiciously small
        raise HTTPException(status_code=400, detail="Image appears too small or corrupted.")

    logger.info(f"Vision diagnosis request: crop={crop_name}, region={region}, size={len(image_bytes)} bytes")

    diagnosis = await vision_diagnosis_service.diagnose_from_bytes(
        image_bytes=image_bytes,
        mime_type=image.content_type,
        crop_name=crop_name,
        region=region
    )

    return {
        "success": True,
        "diagnosis": diagnosis
    }


@router.post("/diagnose-base64", response_model=Dict[str, Any])
async def diagnose_from_base64(
    payload: Dict[str, Any]
):
    """
    Submit a base64-encoded crop image for AI disease diagnosis.

    Request body:
    ```json
    {
        "image_base64": "<base64 string>",
        "mime_type": "image/jpeg",
        "crop_name": "Rice",
        "region": "Maharashtra"
    }
    ```
    """
    image_b64 = payload.get("image_base64")
    if not image_b64:
        raise HTTPException(status_code=400, detail="Missing 'image_base64' field.")

    diagnosis = await vision_diagnosis_service.diagnose_from_base64(
        base64_image=image_b64,
        mime_type=payload.get("mime_type", "image/jpeg"),
        crop_name=payload.get("crop_name"),
        region=payload.get("region")
    )

    return {
        "success": True,
        "diagnosis": diagnosis
    }
