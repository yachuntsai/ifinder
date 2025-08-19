from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    url_path = Column(
        String, nullable=False
    )  # served by StaticFiles at /images/<filename>
    embedding = Column(JSONB, nullable=True)  # store vector as JSON array
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    feedback = relationship(
        "Feedback", back_populates="image", cascade="all, delete-orphan"
    )
