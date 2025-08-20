"""Feedback Schema for iFinder Application
This module defines the Pydantic schemas for feedback-related data structures
used in the iFinder application.
"""

from typing import Optional

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""

    query_text: str
    image_id: int
    is_good: bool
    score: Optional[float] = None


class FeedbackResponse(BaseModel):
    """Response model for feedback data."""

    id: int
    query: str
    image_id: int
    is_good: bool
    score: Optional[float] = None
    created_at: str
