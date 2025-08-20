"""Database Base Module
This module sets up the SQLAlchemy base and engine for the application.
It also registers the pgvector extension for vector support in PostgreSQL.
"""

from app.core.config import settings
from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # log SQL queries if debug = True
)


@event.listens_for(engine, "connect")
def _register_vector(dbapi_conn, _):
    register_vector(dbapi_conn)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.close()
