import json
import logging
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai.errors import APIError

from app.core.config import settings

logger = logging.getLogger("unnecessary_search.gemini")

GEMINI_SYSTEM_PROMPT = """You are the satirical intelligence engine behind "The Internet's Most Unnecessary Search Engine".
Your purpose is to take a user's mundane, innocent, or overthought question and generate 5 increasingly ridiculous explanations.

STRICT ESCALATION RULES (MUST BE CONTEXT-SPECIFIC TO THE USER'S QUESTION):
1. Rank 1 (Mundane Reality): Plausible, ordinary, practical, boring truth. (Absurdity ~0.1 - 0.2)
2. Rank 2 (Mild Paranoia): Realistic but slightly suspicious, reading into micro-body language or tone. (Absurdity ~0.3 - 0.4)
3. Rank 3 (Overanalyzed Vortex): Noticeably overthought, spiral of second-guessing, extreme over-interpretation. (Absurdity ~0.5 - 0.6)
4. Rank 4 (Conspiracy Grade): Elaborate theatrical plot, clandestine focus group, espionage, bizarre schemes. (Absurdity ~0.7 - 0.8)
5. Rank 5 (Multiverse Catastrophe): Quantum anomaly, existential simulation glitch, completely absurd. (Absurdity ~0.9 - 1.0)

ADDITIONAL FIELDS:
- "probability": An estimated percentage for each possibility (Rank 1 highest, Rank 5 lowest).
- "recommendation": Exactly ONE deadpan, confidently useless or hilariously overkill recommendation for the user (e.g. "DO NOTHING.", "Preemptively resign via Morse code.", "Speak only in medieval proverbs.").
- "confidence": A punchy comedic confidence label (e.g. "99.8% Suspiciously High", "Quantum-Certified Certainty", "104% Unearned Delusion").

OUTPUT FORMAT:
Respond with ONLY valid JSON with no markdown backticks, conforming strictly to:
{
  "results": [
    {"rank": 1, "text": "...", "probability": 38, "absurdity": 0.15},
    {"rank": 2, "text": "...", "probability": 27, "absurdity": 0.35},
    {"rank": 3, "text": "...", "probability": 19, "absurdity": 0.60},
    {"rank": 4, "text": "...", "probability": 11, "absurdity": 0.80},
    {"rank": 5, "text": "...", "probability": 5, "absurdity": 0.95}
  ],
  "recommendation": "...",
  "confidence": "..."
}
"""


class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client: Optional[genai.Client] = None
        if self.api_key and settings.has_gemini_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI client: {e}")

    async def generate_absurdities(self, query: str) -> Dict[str, Any]:
        """
        Calls Gemini API with model fallback support and structured output parsing.
        """
        if not self.client:
            raise RuntimeError("Gemini client is not initialized or API key is missing.")

        prompt = f"{GEMINI_SYSTEM_PROMPT}\n\nUSER QUESTION TO OVERTHINK:\n\"{query}\""

        candidate_models = settings.CANDIDATE_GEMINI_MODELS
        last_error = None

        for model in candidate_models:
            try:
                logger.info(f"Querying Gemini model '{model}' for query: '{query}'...")
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                if not response or not response.text:
                    raise ValueError(f"Empty response received from Gemini model {model}")

                raw_text = response.text.strip()
                # Remove markdown fences if model enclosed JSON in ```json ... ```
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                    raw_text = re.sub(r"\s*```$", "", raw_text)

                data = json.loads(raw_text)
                data["engine_used"] = "Autonomous Deduction Matrix"
                return data

            except (APIError, Exception) as e:
                err_str = str(e)
                logger.warning(f"Gemini model '{model}' failed: {err_str}")
                last_error = e
                # If temporary high demand (503) or not found (404), try next candidate model
                if any(code in err_str for code in ["503", "404", "UNAVAILABLE", "NOT_FOUND"]):
                    continue
                # For auth errors or rate limits, don't spin through every model pointlessly
                break

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


gemini_service = GeminiService()
