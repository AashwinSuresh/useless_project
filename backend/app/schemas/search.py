from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="The overthought everyday question to analyze",
        examples=["Why did my friend say 'k'?"],
        max_length=500,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Search query cannot be empty or solely whitespace.")
        return stripped


class SearchResult(BaseModel):
    rank: int = Field(..., description="Escalation rank 1 to 5", ge=1, le=5)
    text: str = Field(..., description="The humorous explanation text")
    probability: int = Field(..., description="Comedic probability percentage (0-100)", ge=0, le=100)
    absurdity: float = Field(..., description="Absurdity rating on a scale of 0.0 (plausible) to 1.0 (quantum catastrophe)", ge=0.0, le=1.0)
    tier: Optional[int] = Field(None, description="Paranoia Tier level 1-5")
    title: Optional[str] = Field(None, description="Paranoia Tier descriptive title")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    results: List[SearchResult] = Field(..., description="Exactly 5 escalating explanations")
    possibilities: List[SearchResult] = Field(..., description="Backwards-compatible alias for results")
    recommendation: str = Field(..., description="Humorous, confidently useless recommended action")
    recommended_action: str = Field(..., description="Backwards-compatible alias for recommendation")
    confidence: str = Field(..., description="Comedic confidence assessment")
    uselessness_score: int = Field(..., description="Calculated futility index percentage (0-100)", ge=0, le=100)
    engine: str = Field(..., description="Inference engine used (e.g. Gemini 2.5 Flash, Offline Paranoia Oracle)")
