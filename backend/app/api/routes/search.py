import logging
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.schemas.search import SearchRequest, SearchResponse
from app.services.gemini import gemini_service
from app.services.search_engine import (
    calculate_uselessness_score,
    generate_offline_fallback,
    process_search_results,
)

logger = logging.getLogger("unnecessary_search.routes")
router = APIRouter()


async def execute_search(request: SearchRequest) -> SearchResponse:
    query = request.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty."
        )

    raw_data = None
    engine_name = "Autonomous Deduction Matrix"

    # 1. Attempt inference with Google Gemini if configured
    if settings.has_gemini_key:
        try:
            logger.info("Dispatching query to Gemini service...")
            raw_data = await gemini_service.generate_absurdities(query)
            engine_name = raw_data.get("engine_used", "Autonomous Deduction Matrix")
        except Exception as e:
            logger.warning(f"Inference service unavailable ({e}). Engaging internal matrix.")

    # 2. Engage context-sensitive offline fallback if no key or Gemini error
    if not raw_data:
        logger.info("Using context-aware Offline Absurdity Engine.")
        raw_data = generate_offline_fallback(query)
        engine_name = raw_data.get("engine_used", "Autonomous Deduction Matrix")

    raw_items = raw_data.get("results") or raw_data.get("possibilities") or []
    processed_results = process_search_results(raw_items)

    recommendation = raw_data.get(
        "recommendation"
    ) or raw_data.get(
        "recommended_action"
    ) or "DO NOTHING."

    confidence = raw_data.get("confidence") or "99.8% Suspiciously High"
    uselessness_score = calculate_uselessness_score(processed_results, recommendation)

    return SearchResponse(
        query=query,
        results=processed_results,
        possibilities=processed_results,
        recommendation=recommendation,
        recommended_action=recommendation,
        confidence=confidence,
        uselessness_score=uselessness_score,
        engine=engine_name
    )


@router.post("/search", response_model=SearchResponse, summary="Analyze an innocent question (Standard)")
async def search_standard(request: SearchRequest):
    return await execute_search(request)


@router.post("/api/search", response_model=SearchResponse, summary="Analyze an innocent question (API Route)")
async def search_api(request: SearchRequest):
    return await execute_search(request)
