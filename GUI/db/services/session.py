import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from GUI.db.base import Base


# CONFIG
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL can't be 'None'.")

engine = create_engine(
    DATABASE_URL, future=True, echo=False, pool_pre_ping=True
)  # évite connexions mortes

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# SESSION UTILS
def get_db_session() -> Generator[Session, None, None]:
    """
    Fournit une session DB.

    Usage FastAPI (dependency injection) :
        def endpoint(db: Session = Depends(get_db_session)):

    Usage script / service :
        with get_db_session_ctx() as db:
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class get_db_session_ctx:
    """
    Context manager explicite pour usage hors FastAPI.
    """

    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()
