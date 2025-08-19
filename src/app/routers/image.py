from pathlib import Path
from typing import List

import numpy as np
from app.core.config import settings
from app.core.database import get_db
from app.db.models.image import Image
from app.ml import clip
from app.schemas.image import (
    ImageMatchingResponse,
    ImageResponse,
    ImagesSummaryResponse,
    SearchResponse,
)
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

IMAGE_ENDPOINT_PREFIX = "/images"
router = APIRouter(prefix=IMAGE_ENDPOINT_PREFIX, tags=["image"])

DATA_DIR = settings.data_dir
IMAGES_DIR = Path(settings.images_dir)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
RAW_IMAGE_ENDPOINT = "/raw"
router.mount(RAW_IMAGE_ENDPOINT, StaticFiles(directory=str(IMAGES_DIR)), name="raw")


@router.post("/ingestions")
def index_from_folder(folder: str = Form(...), db: Session = Depends(get_db)):
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
        url_path = f"{IMAGE_ENDPOINT_PREFIX}{RAW_IMAGE_ENDPOINT}/{filename}"
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
    total_images = db.query(Image).count()
    return ImagesSummaryResponse(total=total_images)


@router.get("/search", response_model=SearchResponse)
def search(query: str, top_k: int = 1, db: Session = Depends(get_db)):
    items = db.query(Image).filter(Image.embedding.isnot(None)).all()
    if not items:
        raise HTTPException(
            status_code=400,
            detail="No images indexed. Use /index_from_folder or /index_from_zip first.",
        )
    text_vec = clip.embed_text(clip.get_model_context(), query)
    mat = np.array([it.embedding for it in items], dtype=np.float32)
    scores = mat @ text_vec.astype(np.float32)
    top_k = max(1, min(top_k, len(items)))
    idxs = np.argsort(-scores)[:top_k]
    results = []
    for i in idxs:
        it = items[int(i)]
        results.append(
            ImageMatchingResponse(
                id=it.id,
                filename=it.filename,
                url=it.url_path,
                score=float(scores[int(i)]),
            )
        )
    return SearchResponse(query=query, results=results)


@router.get("/", response_model=List[ImageResponse])
def get_images(db: Session = Depends(get_db)):
    items = db.query(Image).all()
    return [
        ImageResponse(id=item.id, filename=item.filename, url=item.url_path)
        for item in items
    ]
