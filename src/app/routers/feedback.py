import os
from pathlib import Path
from typing import List

import numpy as np
from app.core.database import Base, engine, get_db
from app.db.models.feedback import Feedback
from app.db.models.image import Image
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/feedbacks", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    image = db.query(Image).get(req.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    fb = Feedback(
        query_text=req.query_text,
        image_id=image.id,
        is_good=req.is_good,
        score=req.score,
    )
    db.add(fb)
    db.commit()
    return FeedbackResponse(
        id=fb.id,
        query=fb.query_text,
        image_id=fb.image_id,
        is_good=fb.is_good,
        score=fb.score,
        created_at=fb.created_at.isoformat(),
    )


@router.get("", response_model=List[FeedbackResponse])
def get_feedbacks(image_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Feedback)
    if image_id:
        query = query.filter(Feedback.image_id == image_id)
    feedbacks = query.all()
    return [
        FeedbackResponse(
            id=fb.id,
            query=fb.query_text,
            image_id=fb.image_id,
            is_good=fb.is_good,
            score=fb.score,
            created_at=fb.created_at.isoformat(),
        )
        for fb in feedbacks
    ]
