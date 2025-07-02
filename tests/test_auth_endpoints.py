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


def test_signup_and_login(client):
    signup_payload = {"username": "alice", "password": "secret"}
    response = client.post("/signup", json=signup_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["role"] == "user"
    assert "id" in data

    response = client.post("/login", json=signup_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data


def test_token_refresh(client):
    payload = {"username": "bob", "password": "pass"}
    client.post("/signup", json=payload)
    login_resp = client.post("/login", json=payload)
    access_token = login_resp.json()["access_token"]

    refresh_resp = client.post("/refresh", headers={"Authorization": f"Bearer {access_token}"})
    assert refresh_resp.status_code == 200
    new_token = refresh_resp.json()["access_token"]
    assert new_token


def test_admin_route_access(client):
    # create admin user
    admin_creds = {"username": "admin", "password": "adminpass", "role": "admin"}
    client.post("/signup", json=admin_creds)
    login_resp = client.post("/login", json=admin_creds)
    admin_token = login_resp.json()["access_token"]

    resp = client.get("/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": "Welcome admin!"}

    # normal user should not access admin route
    user_creds = {"username": "user", "password": "userpass"}
    client.post("/signup", json=user_creds)
    login_resp = client.post("/login", json=user_creds)
    user_token = login_resp.json()["access_token"]
    resp = client.get("/admin", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 403


def test_login_wrong_credentials(client):
    creds = {"username": "eve", "password": "good"}
    client.post("/signup", json=creds)

    bad_payload = {"username": "eve", "password": "bad"}
    resp = client.post("/login", json=bad_payload)
    assert resp.status_code == 401


def test_get_current_user(client):
    creds = {"username": "mallory", "password": "topsecret"}
    signup_resp = client.post("/signup", json=creds)
    user_data = signup_resp.json()

    login_resp = client.post("/login", json=creds)
    token = login_resp.json()["access_token"]

    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["id"] == user_data["id"]
    assert me["username"] == creds["username"]
