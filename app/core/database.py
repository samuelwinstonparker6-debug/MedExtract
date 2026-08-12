import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLite: no pool args (unsupported); PostgreSQL: use connection pool settings
if settings.DATABASE_URL.startswith('sqlite'):
    logger.warning(
        'Using SQLite — suitable for development only. '
        'Set DATABASE_URL to a PostgreSQL connection string in production.'
    )
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={'check_same_thread': False},
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,   # Detect and recover stale connections
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a database session and guarantees close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
