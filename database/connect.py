import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

logging.getLogger('sqlalchemy').setLevel(logging.WARN)


def get_session(db_url: str) -> Session:
    engine = create_engine(db_url, echo=True)
    session_local = sessionmaker(engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(engine)

    return session_local()
