import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_unhandled_exception_returns_json(client):
    resp = client.get("/error")
    assert resp.status_code == 500
    assert resp.json() == {"error": "Internal server error"}
