"""Router for image-related endpoints in the iFinder application."""

from pathlib import Path
from typing import List

import numpy as np
from app.core.config import settings
from app.db.base import get_db
from app.db.models.image import Image
from app.ml import clip
from app.schemas.image import (
    ImageMatchingResponse,
    ImageResponse,
    ImagesSummaryResponse,
    SearchResponse,
)
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

IMAGE_ENDPOINT_PREFIX = "/images"
router = APIRouter(prefix=IMAGE_ENDPOINT_PREFIX, tags=["image"])

DATA_DIR = settings.data_dir
IMAGES_DIR = Path(settings.images_dir)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
RAW_IMAGE_ENDPOINT = "/static/image"


@router.post("/ingestions", response_model=List[ImageResponse])
def ingest_from_folder(folder: str = Form(...), db: Session = Depends(get_db)):
    """Ingest images from a specified folder into the database."""
    folder_path = Path(folder)
    if not folder_path.exists():
        raise HTTPException(status_code=400, detail=f"Folder not found: {folder}")
    image_paths: List[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.gif"):
        image_paths.extend(sorted(folder_path.glob(ext)))
    if not image_paths:
        raise HTTPException(status_code=400, detail="No images found in folder.")

    existing_items = (
        db.query(Image).filter(Image.filename.in_([p.name for p in image_paths])).all()
    )
    existing_filenames = {item.filename for item in existing_items}

    dest_paths = []
    for src in image_paths:
        if src.name in existing_filenames:
            continue
        dest = IMAGES_DIR / src.name
        if src.resolve() != dest.resolve():
            dest.write_bytes(src.read_bytes())
        dest_paths.append(dest)

    if not dest_paths:
        raise HTTPException(status_code=400, detail="No new images to index.")

    batch = 32
    all_embeddings = []
    for i in range(0, len(dest_paths), batch):
        embs = clip.embed_images(
            clip.get_model_context(), [str(p) for p in dest_paths[i : i + batch]]
        )
        all_embeddings.append(embs)
    embeddings = np.vstack(all_embeddings).tolist()

    results = []
    for path, emb in zip(dest_paths, embeddings):
        filename = path.name
        url_path = f"http://localhost:8000{RAW_IMAGE_ENDPOINT}/{filename}"
        results.append(Image(filename=filename, url_path=url_path, embedding=emb))
        db.add_all(results)
        db.flush()  # <-- allocate primary keys for all rows

    db.commit()
    return [
        ImageResponse(id=item.id, filename=item.filename, url=item.url_path)
        for item in results
    ]


@router.get("/summary", response_model=ImagesSummaryResponse)
def get_images_summary(db: Session = Depends(get_db)):
    """Get a summary of all indexed images."""
    total_images = db.query(Image).count()
    return ImagesSummaryResponse(total=total_images)


@router.get("/search", response_model=SearchResponse)
def search(query: str, top_k: int = 1, db: Session = Depends(get_db)):
    """Search for images matching a text query using CLIP embeddings."""
    # 1) embed the query (same as before)
    text_vec = clip.embed_text(clip.get_model_context(), query)
    qvec = text_vec.tolist()  # pgvector handles Python lists/ndarrays

    # 2) build a query that orders by cosine distance ASC (smaller = closer)
    #    and also compute a "score" = 1 - distance to match cosine similarity
    stmt = (
        select(Image, (1 - Image.embedding.cosine_distance(qvec)).label("score"))
        .where(Image.embedding.isnot(None))
        .order_by(Image.embedding.cosine_distance(qvec))  # nearest first
        .limit(max(1, top_k))
    )

    rows = db.execute(stmt).all()  # list of (Image, score)
    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No images indexed. Use /index_from_folder or /index_from_zip first.",
        )

    results = [
        ImageMatchingResponse(
            id=img.id,
            filename=img.filename,
            url=img.url_path,
            score=float(score),
        )
        for (img, score) in rows
    ]
    return SearchResponse(query=query, results=results)


@router.get("/", response_model=List[ImageResponse])
def get_images(db: Session = Depends(get_db)):
    """Get a list of all indexed images."""
    items = db.query(Image).all()
    return [
        ImageResponse(id=item.id, filename=item.filename, url=item.url_path)
        for item in items
    ]
