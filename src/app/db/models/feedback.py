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


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    score = Column(Float, nullable=True)

    is_good = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    image = relationship("Image", back_populates="feedback")
