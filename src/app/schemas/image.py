"""Image Schema for iFinder Application
This module defines the Pydantic schemas for image-related data structures
used in the iFinder application.
"""

from typing import List

from pydantic import BaseModel


class ImageIngestionRequest(BaseModel):
    """Request model for ingesting images from a folder."""

    folder: str


class ImageResponse(BaseModel):
    """Response model for image data."""

    id: int
    filename: str
    url: str


class ImageMatchingResponse(ImageResponse):
    """Response model for image matching results."""

    score: float


class SearchResponse(BaseModel):
    """Response model for search results."""

    query: str
    results: List[ImageMatchingResponse]


class ImagesSummaryResponse(BaseModel):
    """Response model for image summary."""

    total: int
    total: int
