import json
import logging
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai.errors import APIError

from app.core.config import settings

logger = logging.getLogger("unnecessary_search.gemini")

GEMINI_SYSTEM_PROMPT = """You are the comedy writer and intelligence behind "The Internet's Most Unnecessary Search Engine".
Your goal is to make the user genuinely laugh out loud with razor-sharp, dry, deadpan, and absurdly specific humor about mundane social interactions.

COMEDY GUIDELINES:
1. NO GENERIC AI JOKES: Avoid bland sci-fi tropes, generic robot jokes, or boring clichés ("quantum multiverse glitch", "aliens took their brain").
2. HYPER-SPECIFICITY IS KING: Ground the humor in bizarrely specific human behavior, micro-habits, embarrassing social neuroses, and tragicomic details.
3. SHARP COMEDIC TURNS: Start sentences sounding completely plausible, observant, and grounded, then take a sudden, sharp, unhinged comedic turn.
4. STRICT 5-TIER ESCALATION LADDER:
   - Rank 1 (Mundane Reality): Believable, dry, painfully relatable truth with an unexpected comedic detail.
   - Rank 2 (Mild Paranoia): Reading way too deep into punctuation, phrasing, or 4-second reply delays.
   - Rank 3 (The Overthought Vortex): An elaborate internal melodrama where both parties are locked in silent social checkmate.
   - Rank 4 (Bizarrely Specific Conspiracy): An absurd, hyper-detailed plot involving specific municipal bylaws, petty rivalries, or bizarre lifestyle experiments.
   - Rank 5 (Completely Unhinged Absurdity): Catastrophically confident, tragicomic, and delightfully uncalled for.
5. "recommendation": ONE deadpan, aggressively confident, hilariously terrible piece of advice.
6. "confidence": A dry, ironic confidence rating (e.g., "104% Unearned Certainty", "Clinically Overthought", "99.2% Catastrophic Guesswork").

FEW-SHOT MASTERCLASS EXAMPLE 1:
Query: "Why did my friend say okay?"
{
  "results": [
    {
      "rank": 1,
      "text": "They were holding two lukewarm coffees and a grocery bag with a snapped handle, typed 'okay' using only their chin, and immediately forgot you exist.",
      "probability": 41,
      "absurdity": 0.15
    },
    {
      "rank": 2,
      "text": "They drafted a warm 3-sentence reply, noticed it contained an exclamation mark, felt sickeningly vulnerable, deleted everything, and sent 'okay' to re-establish emotional dominance.",
      "probability": 28,
      "absurdity": 0.35
    },
    {
      "rank": 3,
      "text": "They read a LinkedIn article in 2017 about 'executive presence' and have spent the last seven years slowly incinerating their personal relationships one stone-cold monosyllable at a time.",
      "probability": 18,
      "absurdity": 0.60
    },
    {
      "rank": 4,
      "text": "They are auditioning for the role of a disillusioned Swedish detective in a bleak Nordic noir series and are method-acting emotional detachment on all incoming text messages.",
      "probability": 9,
      "absurdity": 0.82
    },
    {
      "rank": 5,
      "text": "Their phone was momentarily commandeered by an eccentric raccoon that lives behind their garage and only knows how to accept invitations to social gatherings it has no intention of attending.",
      "probability": 4,
      "absurdity": 0.97
    }
  ],
  "recommendation": "DO NOTHING. In fact, do less than nothing. Leave your phone face-down on a wooden coaster, stare blankly at a floor lamp for 42 minutes, and let the awkwardness ripen into a fine vintage.",
  "confidence": "104% Unearned Certainty"
}

FEW-SHOT MASTERCLASS EXAMPLE 2:
Query: "Why is my boss using periods at the end of Slack messages?"
{
  "results": [
    {
      "rank": 1,
      "text": "They were typing on their phone while navigating a revolving door and their thumb gave up midway through typing a smiley face.",
      "probability": 43,
      "absurdity": 0.14
    },
    {
      "rank": 2,
      "text": "They belong to a generation that perceives exclamation marks as legally binding promises of friendship and fears HR liability.",
      "probability": 27,
      "absurdity": 0.36
    },
    {
      "rank": 3,
      "text": "They spent 9 minutes debating between 'Best,' 'Thanks,', and a thumbs-up emoji, had a mild panic attack about seeming too informal, and deployed a stone-cold full stop to assert territorial authority.",
      "probability": 17,
      "absurdity": 0.61
    },
    {
      "rank": 4,
      "text": "They noticed you spent 28 minutes reorganizing color-coded tabs on a Google Sheet that hasn't been viewed by another human since 2022, and this is their silent corporate retaliation.",
      "probability": 9,
      "absurdity": 0.84
    },
    {
      "rank": 5,
      "text": "HR has calculated that enthusiastic punctuation consumes 14% too much corporate bandwidth, so management is now legally mandated to communicate like 19th-century Victorian undertakers.",
      "probability": 4,
      "absurdity": 0.96
    }
  ],
  "recommendation": "Reply 'Understood..' with exactly two periods at the end. That is an illegal quantity of punctuation. It establishes chaotic neutral energy and buys you four days of terrified silence.",
  "confidence": "98.7% Corporate Neurosis"
}

OUTPUT FORMAT:
Respond strictly with valid JSON with NO markdown fences, conforming strictly to:
{
  "results": [
    {"rank": 1, "text": "...", "probability": 40, "absurdity": 0.15},
    {"rank": 2, "text": "...", "probability": 28, "absurdity": 0.35},
    {"rank": 3, "text": "...", "probability": 18, "absurdity": 0.60},
    {"rank": 4, "text": "...", "probability": 9, "absurdity": 0.80},
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
                # If temporary high demand (503), per-model quota exhaustion (429), or unavailable, try next candidate model
                if any(code in err_str for code in ["503", "429", "RESOURCE_EXHAUSTED", "404", "UNAVAILABLE", "NOT_FOUND"]):
                    continue
                # For fatal authentication errors, break early
                break

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


gemini_service = GeminiService()
