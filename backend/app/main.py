"""FastAPI application exposing the feedback sentiment analysis endpoint."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .graph import run_feedback_workflow
from .schemas import FeedbackAnalysisResponse, FeedbackRequest


settings = get_settings()

app = FastAPI(title="Feedback Sentiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/feedback/analyze", response_model=FeedbackAnalysisResponse)
async def analyze_feedback(request: FeedbackRequest) -> FeedbackAnalysisResponse:
    """Analyze customer feedback and return summary and sentiment."""
    try:
        result = run_feedback_workflow(request.text)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Failed to analyze feedback") from exc

    return result

