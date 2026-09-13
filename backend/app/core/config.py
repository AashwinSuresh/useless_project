import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Search for .env in current, backend, or parent directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_candidates = [
    Path.cwd() / ".env",
    BASE_DIR / ".env",
    BASE_DIR.parent / ".env",
]

for p in env_candidates:
    if p.is_file():
        load_dotenv(dotenv_path=p)
        break


class Settings:
    PROJECT_NAME: str = "The Internet's Most Unnecessary Search Engine"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = (
        "AI-Powered Parody Search Engine that overanalyzes everyday innocent questions "
        "with escalating absurdity, probability normalization, and unnecessary recommendations."
    )

    # API Keys - Server-Side Only
    GEMINI_API_KEY: str = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("API_KEY")
        or ""
    ).strip()

    # Model settings
    DEFAULT_GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    CANDIDATE_GEMINI_MODELS: List[str] = [
        "gemini-2.5-flash",
        "gemini-3.6-flash"
    ]

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"
    ]

    @property
    def has_gemini_key(self) -> bool:
        dummy_keys = {"your_gemini_api_key_here", "your_key_here", ""}
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY not in dummy_keys)

    def mask_key(self) -> str:
        if not self.has_gemini_key:
            return "NO_KEY"
        k = self.GEMINI_API_KEY
        if len(k) <= 8:
            return "****"
        return f"{k[:6]}...****"


settings = Settings()
