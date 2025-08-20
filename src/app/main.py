"""Main application entry point for the FastAPI server."""

from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.base import Base, engine
from app.routers import feedback, image
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


# Optional: warm up CLIP on startup (so first request is fast)
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan event to initialize resources."""
    try:
        # Lazy import to avoid import cost when not starting the server
        from app.ml import clip

        clip.get_model_context().get_model()
        yield
    finally:
        # If you keep any global handles, close them here
        pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    Base.metadata.create_all(bind=engine)

    # Routers
    app.include_router(image.router)
    app.include_router(feedback.router)

    app.mount(
        image.RAW_IMAGE_ENDPOINT,
        StaticFiles(directory=str(image.IMAGES_DIR)),
        name="image",
    )

    # Simple health check
    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app


app = create_app()
