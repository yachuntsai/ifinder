"""Image Model"""

from datetime import datetime, timezone

from app.db.base import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class Image(Base):
    """Image model for storing image metadata and embeddings."""

    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    url_path = Column(String, nullable=False)
    embedding = Column(Vector(512))  # CLIP ViT-B/32

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    feedbacks = relationship(
        "Feedback", back_populates="image", cascade="all, delete-orphan"
    )
