from typing import List

from pydantic import BaseModel, Field


class ImageResponse(BaseModel):
    id: int
    filename: str
    url: str


class ImageMatchingResponse(ImageResponse):
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[ImageMatchingResponse]


class ImagesSummaryResponse(BaseModel):
    total: int
    total: int
