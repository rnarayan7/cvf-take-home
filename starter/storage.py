from __future__ import annotations
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from .models import Base

DB_URL = "sqlite:///cvf.db"

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

def init_db():
    Base.metadata.create_all(engine)
