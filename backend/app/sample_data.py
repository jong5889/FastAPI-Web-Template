"""Utilities for loading sample data into the database."""

from pathlib import Path
import json
from sqlalchemy.orm import Session

from .database import SessionLocal, Base, engine
from .crud import create_user
from .schemas import UserCreate


DEFAULT_PATH = Path(__file__).resolve().parents[1] / "sample_data.json"


def load_sample_data(db: Session, path: Path = DEFAULT_PATH) -> None:
    """Load users from the given JSON file into the database."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for user_data in data.get("users", []):
        create_user(db, UserCreate(**user_data))


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        load_sample_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
