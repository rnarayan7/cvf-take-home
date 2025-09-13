from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import structlog
from dotenv import load_dotenv
from src.python.db.schemas import Base

load_dotenv()

logger = structlog.get_logger(__file__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cvf.db")

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def init_database():
    """Initialize database with tables"""
    logger.info("Creating database tables")
    create_tables()
    logger.info("Database tables created successfully")
    logger.info("Database initialization completed")
