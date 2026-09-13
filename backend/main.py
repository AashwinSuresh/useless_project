import os
import re
import json
import random
import logging
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import httpx

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unnecessary_search")

app = FastAPI(
    title="The Internet's Most Unnecessary Search Engine API",
    description="Backend API powered by FastAPI, Gemini/Grok LLM, and Absurd Offline Fallback.",
    version="1.0.0",
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for local hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="The overthought question to analyze",
        example="Why did my friend say 'k'?",
    )


class Possibility(BaseModel):
    tier: Optional[int] = Field(None, description="Paranoia Tier 1-5")
    title: Optional[str] = Field(None, description="Tier title")
    text: str = Field(..., description="Explanation possibility")
    probability: int = Field(..., description="Comedic probability (0-100)")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    possibilities: List[Possibility] = Field(
        ..., description="List of exactly 5 escalating possibilities"
    )
    recommended_action: str = Field(
        ..., description="Humorous recommended action"
    )
    confidence: str = Field(..., description="Comedic confidence label")
    engine: str = Field(
        default="AI Multiverse Core",
        description="Engine used (Gemini, Grok, or Offline Oracle)"
    )


def normalize_probabilities(possibilities: list) -> List[dict]:
    """
    Ensure exactly 5 possibilities exist and their probabilities sum to exactly 100.
    """
    tier_titles = [
        "Mundane Reality",
        "Mild Paranoia",
        "Overanalyzed Vortex",
        "Conspiracy Grade",
        "Multiverse Catastrophe"
    ]

    while len(possibilities) < 5:
        idx = len(possibilities)
        possibilities.append({
            "text": "A clandestine organization is orchestrating an elaborate psychological experiment.",
            "probability": 1
        })
    possibilities = possibilities[:5]

    for i, item in enumerate(possibilities):
        item["tier"] = i + 1
        item["title"] = tier_titles[i]

    raw_probs = []
    for item in possibilities:
        p = item.get("probability", 0)
        try:
            val = int(p)
        except (ValueError, TypeError):
            val = 0
        raw_probs.append(max(0, val))

    total = sum(raw_probs)
    if total <= 0:
        default_probs = [38, 27, 18, 12, 5]
        for i in range(5):
            possibilities[i]["probability"] = default_probs[i]
        return possibilities

    if total == 100:
        for i in range(5):
            possibilities[i]["probability"] = raw_probs[i]
        return possibilities

    exact_scaled = [(p / total) * 100.0 for p in raw_probs]
    floored = [int(x) for x in exact_scaled]
    remainder = 100 - sum(floored)

    fractional = [(exact_scaled[i] - floored[i], i) for i in range(5)]
    fractional.sort(key=lambda x: x[0], reverse=True)

    for k in range(remainder):
        idx = fractional[k][1]
        floored[idx] += 1

    for i in range(5):
        possibilities[i]["probability"] = floored[i]

    return possibilities


SYSTEM_PROMPT = """You are the intelligence engine behind "The Internet's Most Unnecessary Search Engine".
Your purpose is to analyze a user's mundane, innocent, or overthought question and generate entertaining, increasingly ridiculous possibilities.

IMPORTANT RULES:
1. The possibilities must be specifically tailored to the context of the user's question.
2. The 5 possibilities MUST strictly escalate in absurdity:
   - Possibility #1 (Mundane Reality): Plausible, ordinary, practical.
   - Possibility #2 (Mild Paranoia): Realistic but slightly suspicious.
   - Possibility #3 (Overanalyzed Vortex): Noticeably overthought, reading way too deep into micro-details.
   - Possibility #4 (Conspiracy Grade): Ridiculous, theatrical, borderline unhinged.
   - Possibility #5 (Multiverse Catastrophe): Completely absurd, existential, quantum conspiracy.
3. Probabilities must be integers between 1 and 100, generally descending from #1 to #5, summing near 100.
4. "recommended_action": Exactly one hilarious, intentionally terrible/overkill action the user should take.
5. "confidence": One punchy humorous confidence rating (e.g., "99.2% Unearned Certainty", "Suspiciously Specific", "Quantum-Certified Delusion").

Respond ONLY with valid JSON conforming to:
{
  "possibilities": [
    {"text": "...", "probability": 40},
    {"text": "...", "probability": 27},
    {"text": "...", "probability": 18},
    {"text": "...", "probability": 11},
    {"text": "...", "probability": 4}
  ],
  "recommended_action": "...",
  "confidence": "..."
}
"""

def generate_offline_absurdities(query: str) -> dict:
    """
    Context-sensitive offline fallback generator for live demos without API keys or on network failure.
    """
    q_lower = query.lower()
    
    # Context-specific templates
    if any(k in q_lower for k in ["'k'", " k ", " k", "text", "message", "reply", "ghost", "left on read"]):
        possibilities = [
            {"text": "They were walking into an elevator or typing while their battery was at 1%.", "probability": 42},
            {"text": "They thought 'ok' sounded too formal and wanted to maintain casual aloofness.", "probability": 28},
            {"text": "They drafted an affectionate 4-paragraph response, panicked, deleted it, and settled on passive-aggressive minimalism.", "probability": 17},
            {"text": "Their phone was intercepted by Russian intelligence who only know how to communicate in monosyllables.", "probability": 9},
            {"text": "The letter 'K' represents the 11th hour of the apocalypse; your friendship has shifted into an alternate timeline where vowels are illegal.", "probability": 4},
        ]
        action = "Draft a 14-page handwritten letter via carrier pigeon demanding clarification on letter capitalization."
        confidence = "98.7% Paranoia Quotient"

    elif any(k in q_lower for k in ["boss", "manager", "work", "email", "slack", "fired", "promotion", "period", "meeting"]):
        possibilities = [
            {"text": "They use standard punctuation on everything because they are over 35 years old.", "probability": 45},
            {"text": "They were rushing between back-to-back quarterly synchronizations and didn't notice the abrupt tone.", "probability": 26},
            {"text": "They noticed you spent 14 minutes looking at Wikipedia instead of updating Jira tickets.", "probability": 16},
            {"text": "HR has already generated an automated replacement clone that drinks less iced coffee.", "probability": 9},
            {"text": "The period at the end of the sentence is an encoded GPS beacon summoning corporate auditors to confiscate your swivel chair.", "probability": 4},
        ]
        action = "Preemptively submit a resignation letter in Morse code, then hide under your desk in high-visibility apparel."
        confidence = "104% Workplace Anxiety"

    elif any(k in q_lower for k in ["dog", "cat", "pet", "staring", "look", "animal"]):
        possibilities = [
            {"text": "There was a microscopic gnat flying two inches past your left shoulder.", "probability": 44},
            {"text": "They are assessing whether you are emotionally stable enough to share cheese.", "probability": 29},
            {"text": "They have detected an ancestral ghost standing directly behind you giving fashion advice.", "probability": 15},
            {"text": "They are transmitting daily telepathic intelligence reports back to the mothership.", "probability": 8},
            {"text": "You are actually the pet in this dimensional simulation, and their annual performance review of you is due today.", "probability": 4},
        ]
        action = "Bow respectfully, sacrifice a slice of cheddar cheese, and avoid making eye contact for 72 hours."
        confidence = "93.4% Interspecies Certainty"

    else:
        # General absurd synthesis using words from the query
        keywords = re.findall(r'\b\w{4,}\b', query)
        kw = keywords[0].capitalize() if keywords else "This Situation"
        kw2 = keywords[1].capitalize() if len(keywords) > 1 else "The Universe"

        possibilities = [
            {"text": f"The most boring explanation is true: circumstances aligned by pure coincidence regarding {kw.lower()}.", "probability": 41},
            {"text": f"Someone noticed your hesitation regarding {kw.lower()} and is reacting cautiously.", "probability": 28},
            {"text": f"An unspoken social script was breached, triggering a silent loop of mutual second-guessing about {kw2.lower()}.", "probability": 18},
            {"text": f"A secretive shadow council decided today was the ideal date to test your coping bandwidth.", "probability": 9},
            {"text": f"A microscopic rift in spacetime swapped your original timeline with one where {kw.lower()} governs the laws of physics.", "probability": 4},
        ]
        action = f"Immediately burn all receipts, delete cache, and speak only in ancient proverbs regarding {kw.lower()}."
        confidence = "99.1% Unearned Certainty"

    return {
        "possibilities": possibilities,
        "recommended_action": action,
        "confidence": confidence,
    }


async def call_gemini(api_key: str, query: str) -> dict:
    """Call Google Gemini API using official SDK or direct endpoint."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"{SYSTEM_PROMPT}\n\nUser Question to Overthink: {query}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        text = response.text.strip()
        # Clean markdown wrappers if model enclosed JSON in ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Google Gemini SDK call failed ({e}). Falling back to REST.")
        # Fallback to direct REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser Question to Overthink: {query}"}]
            }],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload)
            res_json = res.json()
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)


async def call_grok(api_key: str, query: str) -> dict:
    """Call xAI Grok API."""
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("GROK_MODEL", "grok-2-latest"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User query: {query}"}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Grok API returned {response.status_code}: {response.text}")
        res_json = response.json()
        content_str = res_json["choices"][0]["message"]["content"]
        return json.loads(content_str)


# Routes
@app.get("/")
def read_root():
    # If index.html exists in parent workspace directory, serve it!
    index_file = Path(__file__).resolve().parent.parent / "index.html"
    if index_file.exists() and index_file.stat().st_size > 10:
        return FileResponse(index_file)
    return {
        "message": "The Internet's Most Unnecessary Search Engine API",
        "status": "running",
        "endpoints": ["/api/search", "/docs"]
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Unnecessary Search Engine"}


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    query = request.query
    if not isinstance(query, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be a string."
        )

    stripped_query = query.strip()
    if not stripped_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty."
        )

    if len(stripped_query) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query length exceeds maximum limit of 500 characters."
        )

    gemini_key = os.getenv("GEMINI_API_KEY")
    xai_key = os.getenv("XAI_API_KEY")

    data = None
    engine_used = "Offline Paranoia Oracle"

    # 1. Try Gemini if configured
    if gemini_key and gemini_key not in ["your_gemini_api_key_here", "your_key_here", ""]:
        try:
            logger.info("Attempting inference with Gemini...")
            data = await call_gemini(gemini_key, stripped_query)
            engine_used = "Google Gemini 2.5 Flash"
        except Exception as e:
            logger.error(f"Gemini API attempt failed: {e}")

    # 2. Try Grok if Gemini wasn't used or failed
    if not data and xai_key and xai_key not in ["your_grok_api_key_here", "your_key_here", ""]:
        try:
            logger.info("Attempting inference with xAI Grok...")
            data = await call_grok(xai_key, stripped_query)
            engine_used = "xAI Grok 2"
        except Exception as e:
            logger.error(f"Grok API attempt failed: {e}")

    # 3. If no API key or both failed, gracefully fallback to the absurd offline engine!
    if not data:
        logger.info("Using context-aware Offline Absurd Engine (zero-failure mode).")
        data = generate_offline_absurdities(stripped_query)
        engine_used = "Multiverse Quantum Simulator (Offline Engine)"

    raw_possibilities = data.get("possibilities", [])
    normalized_possibilities = normalize_probabilities(raw_possibilities)

    recommended_action = data.get(
        "recommended_action",
        "Lock your front door, change your Wi-Fi name to 'FBI Surveillance Van 4', and pretend to be asleep."
    )
    confidence = data.get("confidence", "99.8% Suspiciously High")

    return SearchResponse(
        query=stripped_query,
        possibilities=[
            Possibility(
                tier=p.get("tier"),
                title=p.get("title"),
                text=p["text"],
                probability=p["probability"]
            )
            for p in normalized_possibilities
        ],
        recommended_action=recommended_action,
        confidence=confidence,
        engine=engine_used
    )
