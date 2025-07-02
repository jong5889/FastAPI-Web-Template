import json
import pytest

pytest.importorskip("fastapi")

from app.sample_data import load_sample_data
from app.database import Base, engine, SessionLocal
from app.models import User


@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_load_sample_data(tmp_path, db):
    data = {"users": [{"username": "joe", "password": "pwd", "role": "user"}]}
    sample_file = tmp_path / "sample.json"
    sample_file.write_text(json.dumps(data))

    load_sample_data(db, path=sample_file)
    users = db.query(User).all()
    assert len(users) == 1
    assert users[0].username == "joe"
    assert users[0].role == "user"
