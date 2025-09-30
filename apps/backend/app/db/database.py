from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use /tmp directory in Lambda for SQLite write permissions
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/eduparent.db"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./eduparent.db"
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()