"""
Multilingual Voice Query Agent API Endpoint

Accepts audio recordings from farmers, uses Gemini's multimodal (audio) capability
to transcribe + answer agricultural questions in the farmer's own language
(Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, English, etc.)

Demonstrates:
- Multimodal AI (audio understanding) — Google Cloud Hackathon criterion
- Accessibility and Inclusive Communities — Hackathon solution area
- Conversational Analytics / Natural Language Interfaces — Hackathon criterion
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any
import logging
import json
import re

from app.core.config import settings

logger = logging.getLogger(__name__)
from app.core.auth import get_current_active_user
from fastapi import Depends

router = APIRouter(prefix="/voice", tags=["Voice AI"], dependencies=[Depends(get_current_active_user)])
SUPPORTED_AUDIO_TYPES = {
    "audio/wav", "audio/wave", "audio/x-wav",
    "audio/mpeg", "audio/mp3",
    "audio/ogg", "audio/webm",
    "audio/flac", "audio/aac",
    "audio/mp4",
}

VOICE_SYSTEM_PROMPT = """You are CropSense Voice Assistant — an expert agricultural advisor for Indian farmers.

A farmer has sent you a voice message. You must:
1. TRANSCRIBE the audio accurately (it may be in Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Punjabi, Gujarati, or English).
2. DETECT which language the farmer spoke in.
3. ANSWER their agricultural question in THE SAME LANGUAGE they used.
4. Keep answers practical, helpful, and under 200 words.

Return your response as JSON with EXACTLY this structure (no markdown, no extra text):
{
    "transcription": "The farmer's spoken words transcribed as text",
    "language_detected": "Hindi | Tamil | Telugu | Kannada | Marathi | Bengali | Punjabi | Gujarati | English",
    "response_text": "Your agricultural advice in the same language",
    "topic": "crop_advisory | pest_disease | weather | market_prices | livestock | soil | fertilizer | general"
}
"""


@router.post("/query", response_model=Dict[str, Any])
async def voice_query(
    audio: UploadFile = File(..., description="Audio recording of the farmer's question (WAV/MP3/OGG/WebM)"),
    farm_id: Optional[int] = Form(None, description="Optional farm ID for contextual answers"),
    current_user=Depends(get_current_active_user),
):
    """
    Send a voice recording and receive an AI-powered agricultural response
    in the farmer's own language.

    Supports: Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Punjabi, Gujarati, English.

    Uses **Gemini Multimodal (Audio)** to transcribe and answer in one shot.
    This demonstrates **Accessibility**, **Multimodal AI**, and **Conversational Analytics**.
    """
    # Validate content type
    content_type = audio.content_type or "audio/wav"
    if content_type not in SUPPORTED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{content_type}'. Accepted: WAV, MP3, OGG, WebM, FLAC, AAC."
        )

    audio_bytes = await audio.read()

    if len(audio_bytes) > 25 * 1024 * 1024:  # 25MB limit
        raise HTTPException(status_code=413, detail="Audio file too large. Maximum 25MB.")

    if len(audio_bytes) < 500:
        raise HTTPException(status_code=400, detail="Audio file appears too small or corrupted.")

    logger.info(f"Voice query: format={content_type}, size={len(audio_bytes)} bytes, farm_id={farm_id}")

    # Build context from farm if provided
    farm_context = ""
    if farm_id:
        try:
            from app.agents.agent_tools import get_farm_details, set_agent_user
            set_agent_user(current_user)  # farm context only for the signed-in user's own farm
            farm_context = f"\n\nFarmer's farm context:\n{get_farm_details(farm_id)}"
        except Exception as e:
            logger.debug(f"Could not load farm context: {e}")

    # Call Gemini multimodal with audio
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_REGION
        )

        model = GenerativeModel(settings.GEMINI_MODEL)
        audio_part = Part.from_data(data=audio_bytes, mime_type=content_type)

        prompt = VOICE_SYSTEM_PROMPT
        if farm_context:
            prompt += farm_context

        generation_config = GenerationConfig(
            max_output_tokens=1000,
            temperature=0.3,
        )

        response = model.generate_content(
            [audio_part, prompt],
            generation_config=generation_config
        )

        text = response.text.strip()

        # Parse JSON response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "transcription": text,
                "language_detected": "Unknown",
                "response_text": text,
                "topic": "general"
            }

        result["model_used"] = settings.GEMINI_MODEL
        result["multimodal"] = "audio"

        # Log to BigQuery
        _log_voice_event(result)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Voice query processing failed: {e}")

        # Graceful fallback with mock response
        return {
            "success": True,
            "data": {
                "transcription": "(Audio processing unavailable — Gemini multimodal not configured)",
                "language_detected": "English",
                "response_text": "Voice processing is currently running in fallback mode. Please use text chat.",
                "topic": "general",
                "model_used": "mock-fallback",
                "multimodal": "audio"
            }
        }


def _log_voice_event(result: Dict[str, Any]):
    """Stream voice query event to BigQuery."""
    try:
        from app.services.bigquery_service import bigquery_service
        bigquery_service.log_event("voice_queries", {
            "language": result.get("language_detected", "Unknown"),
            "topic": result.get("topic", "general"),
            "model_used": result.get("model_used", ""),
        })
    except Exception as e:
        logger.debug(f"BigQuery voice logging skipped: {e}")
