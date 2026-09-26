"""
Vision-based Crop Disease Diagnosis Service using Gemini Multimodal (Vision)

Accepts a crop/leaf image and uses Gemini's multimodal capability to identify
diseases, pests, nutrient deficiencies, and provide treatment recommendations.

Demonstrates: Multimodal AI (text + image understanding) — Google Cloud Hackathon criterion.
"""

import base64
import json
import logging
import re
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class VisionDiagnosisService:
    """Diagnoses crop diseases from images using Gemini Vision (multimodal)."""

    DIAGNOSIS_PROMPT = """You are an expert agricultural plant pathologist AI.
Analyze this image of a crop/plant and provide a diagnosis.

Return a JSON object with EXACTLY this structure (no markdown, no extra text):
{
    "disease_detected": true,
    "disease_name": "Name of disease or 'Healthy' if no disease",
    "scientific_name": "Scientific name if applicable",
    "confidence": 0.0 to 1.0,
    "severity": "none | mild | moderate | severe | critical",
    "affected_part": "leaf | stem | root | fruit | flower | whole_plant",
    "symptoms_observed": ["symptom 1", "symptom 2"],
    "possible_causes": ["cause 1", "cause 2"],
    "treatment": {
        "organic": ["organic treatment 1", "organic treatment 2"],
        "chemical": ["chemical treatment with dosage 1"],
        "cultural": ["cultural practice 1"]
    },
    "prevention": ["prevention step 1", "prevention step 2"],
    "urgency": "low | medium | high | critical",
    "additional_notes": "Any relevant context about crop health"
}

If the image is not of a crop/plant, return:
{"disease_detected": false, "error": "Image does not appear to be a crop or plant."}
"""

    def __init__(self):
        self._model = None
        self._enabled = False
        self._init_model()

    def _init_model(self):
        """Initialize Gemini generative model with vision capability."""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(
                project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_REGION
            )
            self._model = GenerativeModel(settings.GEMINI_MODEL)
            self._enabled = True
            logger.info("VisionDiagnosisService: Gemini Vision model initialized.")
        except Exception as e:
            logger.warning(
                f"VisionDiagnosisService: Gemini Vision init failed: {e}. Running mock mode."
            )
            self._enabled = False

    async def diagnose_from_bytes(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        crop_name: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Diagnose crop disease from raw image bytes.

        Args:
            image_bytes: Raw image bytes (JPEG/PNG/WebP).
            mime_type: MIME type of the image.
            crop_name: Optional crop name for context (e.g. 'Rice', 'Tomato').
            region: Optional region/state for context.

        Returns:
            Structured diagnosis dict.
        """
        context_parts = []
        if crop_name:
            context_parts.append(f"The farmer says this is a {crop_name} plant.")
        if region:
            context_parts.append(f"Located in {region}, India.")
        context = " ".join(context_parts)

        if not self._enabled or not self._model:
            logger.info("VisionDiagnosisService: returning mock diagnosis (Gemini not available).")
            return self._mock_diagnosis(crop_name)

        try:
            from vertexai.generative_models import GenerationConfig, Part

            image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

            full_prompt = self.DIAGNOSIS_PROMPT
            if context:
                full_prompt += f"\n\nAdditional context: {context}"

            generation_config = GenerationConfig(
                max_output_tokens=1500,
                temperature=0.2,
            )

            response = self._model.generate_content(
                [image_part, full_prompt], generation_config=generation_config
            )

            text = response.text.strip()

            # Extract JSON from possible markdown wrapper
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                diagnosis = json.loads(json_match.group())
            else:
                diagnosis = {
                    "disease_detected": False,
                    "error": "Could not parse model response.",
                    "raw": text,
                }

            diagnosis["model_used"] = settings.GEMINI_MODEL
            diagnosis["multimodal"] = True

            # Log to BigQuery
            self._log_diagnosis(diagnosis, crop_name, region)

            return diagnosis

        except Exception as e:
            logger.error(f"VisionDiagnosisService error: {e}")
            return {
                "disease_detected": False,
                "error": f"Diagnosis failed: {str(e)}",
                "model_used": settings.GEMINI_MODEL,
                "multimodal": True,
            }

    async def diagnose_from_base64(
        self,
        base64_image: str,
        mime_type: str = "image/jpeg",
        crop_name: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Diagnose from a base64-encoded image string."""
        image_bytes = base64.b64decode(base64_image)
        return await self.diagnose_from_bytes(image_bytes, mime_type, crop_name, region)

    def _log_diagnosis(self, diagnosis: Dict, crop_name: Optional[str], region: Optional[str]):
        """Stream diagnosis event to BigQuery for analytics."""
        try:
            from app.services.bigquery_service import bigquery_service

            bigquery_service.log_event(
                "vision_diagnoses",
                {
                    "disease_name": diagnosis.get("disease_name", "Unknown"),
                    "confidence": diagnosis.get("confidence", 0),
                    "severity": diagnosis.get("severity", "unknown"),
                    "crop_name": crop_name or "unspecified",
                    "region": region or "unspecified",
                    "model_used": diagnosis.get("model_used", ""),
                },
            )
        except Exception as e:
            logger.debug(f"BigQuery logging skipped: {e}")

    def _mock_diagnosis(self, crop_name: Optional[str] = None) -> Dict[str, Any]:
        """Return a realistic mock diagnosis for development/testing."""
        return {
            "disease_detected": True,
            "disease_name": "Bacterial Leaf Blight",
            "scientific_name": "Xanthomonas oryzae pv. oryzae",
            "confidence": 0.82,
            "severity": "moderate",
            "affected_part": "leaf",
            "symptoms_observed": [
                "Yellow-orange lesions on leaf margins",
                "Wilting of seedlings",
                "Kresek symptom (wilting of leaves)",
            ],
            "possible_causes": [
                "Bacterial infection via contaminated water",
                "High humidity and warm temperatures",
            ],
            "treatment": {
                "organic": [
                    "Apply neem oil spray (5ml/L)",
                    "Use Pseudomonas fluorescens biocontrol agent",
                ],
                "chemical": ["Streptocycline 0.01% + Copper oxychloride 0.25%"],
                "cultural": [
                    "Drain excess water from fields",
                    "Remove and destroy infected plant debris",
                ],
            },
            "prevention": [
                "Use disease-resistant varieties (e.g., IR64, Swarna)",
                "Balanced fertilization — avoid excess nitrogen",
                "Ensure proper field drainage",
            ],
            "urgency": "high",
            "additional_notes": f"Common in {crop_name or 'rice'} during kharif (monsoon) season in India.",
            "model_used": "mock-fallback",
            "multimodal": True,
        }


# Singleton
vision_diagnosis_service = VisionDiagnosisService()
