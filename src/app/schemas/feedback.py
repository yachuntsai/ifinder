from typing import Optional

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    query_text: str
    image_id: int
    is_good: bool
    score: Optional[float] = None


class FeedbackResponse(BaseModel):
    id: int
    query: str
    image_id: int
    is_good: bool
    score: Optional[float] = None
    created_at: str
