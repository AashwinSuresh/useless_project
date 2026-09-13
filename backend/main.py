"""
Root backend entrypoint redirecting to app.main:app
"""
import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
