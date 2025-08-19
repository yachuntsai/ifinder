import os

from app.core.config import settings
from pgvector.psycopg import register_vector  # <-- CHANGED
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)


@event.listens_for(engine, "connect")
def _register_vector(dbapi_conn, _):
    register_vector(dbapi_conn)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.close()
