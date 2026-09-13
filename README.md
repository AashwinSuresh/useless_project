# The Internet's Most Unnecessary Search Engine 🎯

> *"Why find straightforward answers when you can overthink innocent everyday interactions with 99.8% mathematically normalized unearned certainty?"*

A full-stack, parody search engine where users input everyday questions people tend to overthink (e.g., *"Why did my friend say okay?"*). The application generates five increasingly unhinged explanations, normalizes probabilities to strictly 100%, calculates a deterministic **Uselessness Score**, and provides an unnecessarily confident recommendation (*"DO NOTHING."*).

---

## Architecture Overview

```text
React / Modern Web Frontend (frontend/index.html & src/services/api.js)
                      │
                      ▼ HTTP POST /search (or /api/search)
             FastAPI Backend (backend/app/main.py)
                      │
                      ├── Request Validation (Pydantic schemas/search.py)
                      │
                      ▼
             AI Orchestration Layer (backend/app/services/gemini.py)
                      │
                      ├── Google Gemini 2.5 Flash (fallback: 3.6-flash, 1.5-flash)
                      │   (or Offline Paranoia Oracle if offline)
                      │
                      ▼
         Search Engine Service (backend/app/services/search_engine.py)
                      │
                      ├── 5-Tier Probability Normalization (Sum = 100%)
                      ├── Absurdity Calibration (0.0 to 1.0)
                      └── Deterministic Uselessness Score Calculation
                      │
                      ▼
             Structured JSON SearchResponse
                      │
                      ▼
       Frontend Progressive Reveal & Interactive Dossier
       [Cards, Visual Meters, Absurdity Badges, Action, Uselessness Score]
```

---

## Directory Structure

```text
useless_project/
│
├── frontend/
│   ├── index.html               # Premium Absurdism UI (cybernetic radar, cards, gauge)
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js           # Centralized API service with mock mode switch
│   │   └── styles/
│   │       └── main.css         # Design tokens, glassmorphism, responsive grid
│   └── package.json             # Frontend metadata and build hooks
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app assembly, CORS, routes, static mount
│   │   ├── core/
│   │   │   └── config.py        # Settings, environment loader, safe key masking
│   │   ├── schemas/
│   │   │   └── search.py        # Pydantic models (SearchRequest, SearchResult, SearchResponse)
│   │   ├── services/
│   │   │   ├── gemini.py        # Google GenAI service with candidate model fallbacks
│   │   │   └── search_engine.py # Probability normalization, absurdity scoring, uselessness formula
│   │   └── api/
│   │       └── routes/
│   │           └── search.py    # POST /search & POST /api/search handlers
│   ├── main.py                  # Standalone backend launcher
│   ├── requirements.txt         # Backend Python dependencies
│   └── .env.example             # Backend environment template
│
├── .env                         # Server-side environment variables (kept private)
├── .env.example                 # Sanitized template
├── .gitignore                   # Git ignore protecting secrets, cache, and venv
├── test_gemini.py               # Standalone Gemini API connectivity test script
└── README.md                    # Project documentation
```

---

## Environment Configuration

Copy the sanitized template to `.env`:

```bash
cp .env.example .env
```

Configure your environment variables:

```env
# Google Gemini API Key (Server-Side Only - Never Exposed to Browser)
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend API URL configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Default Gemini model (fallbacks: gemini-3.6-flash, gemini-1.5-flash)
GEMINI_MODEL=gemini-2.5-flash
```

> **Zero-Fail Fallback Mode**: If no API key is provided, or during network disruptions, the backend automatically engages the **Offline Paranoia Oracle**, ensuring reliable live demonstrations.

---

## Installation & Running

### 1. Set Up Virtual Environment & Dependencies
```bash
# From the repository root
python -m venv .venv
.\.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Run API Connectivity Verification
```bash
python test_gemini.py
```

### 3. Start the FastAPI Server
```bash
uvicorn app.main:app --app-dir backend --port 8000 --reload
```

### 4. Open the Application
Navigate to `http://localhost:8000/` in your web browser. The backend automatically serves the full-featured **Premium Absurdism** frontend!

---

## API Contract

### Search Endpoint: `POST /search` (and `POST /api/search`)

#### Example Request:
```http
POST /search HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "query": "Why did my friend say okay?"
}
```

#### Example Response:
```json
{
  "query": "Why did my friend say okay?",
  "results": [
    {
      "rank": 1,
      "tier": 1,
      "title": "Mundane Reality",
      "text": "Your friend processed your statement and verbally indicated basic agreement.",
      "probability": 38,
      "absurdity": 0.15
    },
    {
      "rank": 2,
      "tier": 2,
      "title": "Mild Paranoia",
      "text": "The 'okay' was delivered with a micro-pause, signaling mild aloofness.",
      "probability": 27,
      "absurdity": 0.35
    },
    {
      "rank": 3,
      "tier": 3,
      "title": "Overanalyzed Vortex",
      "text": "They chose 'okay' instead of 'sure' as a calibrated test of your emotional stamina.",
      "probability": 19,
      "absurdity": 0.60
    },
    {
      "rank": 4,
      "tier": 4,
      "title": "Conspiracy Grade",
      "text": "The 'okay' was a pre-programmed acoustic trigger for a clandestine psychological study.",
      "probability": 11,
      "absurdity": 0.80
    },
    {
      "rank": 5,
      "tier": 5,
      "title": "Multiverse Catastrophe",
      "text": "A localized spacetime glitch swapped your friend with a parallel version where vowels are illegal.",
      "probability": 5,
      "absurdity": 0.95
    }
  ],
  "recommendation": "DO NOTHING. (Or communicate exclusively via carrier pigeon for 72 hours).",
  "recommended_action": "DO NOTHING.",
  "confidence": "99.4% Suspiciously High",
  "uselessness_score": 86,
  "engine": "Google Gemini (gemini-2.5-flash)"
}
```

### Health Check: `GET /api/health`
```json
{
  "status": "ok",
  "service": "The Internet's Most Unnecessary Search Engine",
  "version": "2.0.0",
  "has_gemini_key": true,
  "key_masked": "AQ.Ab8...****"
}
```

---

## Features

- **5-Tier Escalating Absurdism**:
  - `Tier 1: Mundane Reality` (Boring truth, low absurdity)
  - `Tier 2: Mild Paranoia` (Subtle over-interpretation)
  - `Tier 3: Overanalyzed Vortex` (Mental spiral of second-guessing)
  - `Tier 4: Conspiracy Grade` (Theatrical unhinged schemes)
  - `Tier 5: Multiverse Catastrophe` (Existential simulation glitches)
- **Strict Probability Normalization**: Integer probabilities guaranteed to sum to strictly 100%.
- **Deterministic Uselessness Score**: Computed from absurdity spread and recommendation futility (70% - 99%).
- **Interactive UI**:
  - Web Audio API Synthesizer (procedural retro-futuristic sound effects)
  - Copy Declassified Dossier button with formatted clipboard export
  - Quick query randomizer and pre-loaded overthought dilemma chips
  - Keyboard shortcuts (`Enter` to search, `/` to focus search box, `Esc` to clear)
- **Interactive OpenAPI Documentation**: Available at `http://localhost:8000/docs`.
