"""Pydantic models for API request/response."""

from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request body for feedback analysis."""

    text: str = Field(..., min_length=1, description="Raw customer feedback text")


SentimentType = Literal["HAPPY", "UNHAPPY", "NEUTRAL"]


class FeedbackAnalysisResponse(BaseModel):
    """Response body with analysis results."""

    summary: str = Field(..., description="Summarized feedback")
    sentiment: SentimentType = Field(..., description="Customer sentiment verdict")
    reason: str = Field(default="", description="Explanation for the sentiment verdict")
