import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes.search import router as search_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("unnecessary_search")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# Apply CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(search_router)

# Resolve Frontend Root and Assets
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
LEGACY_INDEX = PROJECT_ROOT / "index.html"

# Mount frontend static directory if exists
frontend_src = FRONTEND_DIR / "src"
if frontend_src.is_dir():
    app.mount("/src", StaticFiles(directory=str(frontend_src)), name="frontend_src")


@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "has_gemini_key": settings.has_gemini_key,
        "key_masked": settings.mask_key(),
    }


@app.get("/", include_in_schema=False)
def serve_index():
    # Prefer frontend/index.html, otherwise fallback to root index.html
    frontend_index = FRONTEND_DIR / "index.html"
    if frontend_index.is_file():
        return FileResponse(frontend_index)
    if LEGACY_INDEX.is_file():
        return FileResponse(LEGACY_INDEX)
    return {
        "message": settings.PROJECT_NAME,
        "status": "running",
        "endpoints": ["/search", "/api/search", "/api/health", "/docs"]
    }


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Gemini API Key configured: {settings.has_gemini_key} ({settings.mask_key()})")
