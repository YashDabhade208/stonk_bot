from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from typing import Any, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

class DatabaseSettings(BaseSettings):
    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_db_url(cls, v: Any):
        if not v:
            raise ValueError("DATABASE_URL is missing in .env file")
        return v


db_settings = DatabaseSettings()

def get_database_url() -> str:
    return str(db_settings.DATABASE_URL)

engine = create_engine(get_database_url(), echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FASTAPI DEPENDENCY
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful!")
        return True
    except SQLAlchemyError as e:
        print("❌ Database connection failed:", e)
        return False
