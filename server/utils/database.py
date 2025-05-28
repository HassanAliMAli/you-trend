import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to a default SQLite DB for local development if DATABASE_URL is not set
    # This is primarily for environments where setting up PostgreSQL might be cumbersome initially.
    # For production, DATABASE_URL pointing to PostgreSQL is expected.
    print("Warning: DATABASE_URL not found in .env. Falling back to SQLite in memory for now.")
    print("Please set up a PostgreSQL database and configure DATABASE_URL in .env for persistence.")
    DATABASE_URL = "sqlite:///./test.db" # In-memory SQLite, or use a file e.g. "sqlite:///./sql_app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # SQLite specific connect_args
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 