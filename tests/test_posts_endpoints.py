import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app
from app import crud


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def get_auth_token(client, username, password):
    signup_payload = {"username": username, "password": password}
    client.post("/signup", json=signup_payload)
    login_resp = client.post("/login", json=signup_payload)
    return login_resp.json()["access_token"]


def test_create_post(client):
    token = get_auth_token(client, "testuser", "testpass")
    user_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = user_resp.json()["id"]

    post_payload = {"title": "My First Post", "content": "This is the content of my first post."}
    response = client.post(f"/users/{user_id}/posts/", json=post_payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == post_payload["title"]
    assert data["content"] == post_payload["content"]
    assert data["owner_id"] == user_id
    assert "id" in data


def test_get_posts(client):
    token = get_auth_token(client, "user1", "pass1")
    user_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = user_resp.json()["id"]

    client.post(f"/users/{user_id}/posts/", json={"title": "Post 1", "content": "Content 1"}, headers={"Authorization": f"Bearer {token}"})
    client.post(f"/users/{user_id}/posts/", json={"title": "Post 2", "content": "Content 2"}, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/posts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Post 1"
    assert data[1]["title"] == "Post 2"


def test_get_single_post(client):
    token = get_auth_token(client, "user2", "pass2")
    user_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = user_resp.json()["id"]

    create_resp = client.post(f"/users/{user_id}/posts/", json={"title": "Single Post", "content": "Single Content"}, headers={"Authorization": f"Bearer {token}"})
    post_id = create_resp.json()["id"]

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Post"


def test_delete_post(client):
    token = get_auth_token(client, "user3", "pass3")
    user_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = user_resp.json()["id"]

    create_resp = client.post(f"/users/{user_id}/posts/", json={"title": "Post to Delete", "content": "Content to delete"}, headers={"Authorization": f"Bearer {token}"})
    post_id = create_resp.json()["id"]

    response = client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Post deleted successfully"}

    # Verify post is deleted
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 404


def test_delete_post_unauthorized(client):
    # User A creates a post
    token_a = get_auth_token(client, "user_a", "pass_a")
    user_a_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token_a}"})
    user_a_id = user_a_resp.json()["id"]
    create_resp = client.post(f"/users/{user_a_id}/posts/", json={"title": "User A Post", "content": "Content A"}, headers={"Authorization": f"Bearer {token_a}"})
    post_id = create_resp.json()["id"]

    # User B tries to delete User A's post
    token_b = get_auth_token(client, "user_b", "pass_b")
    response = client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 403 # Forbidden


def test_create_post_unauthorized_user_id(client):
    token = get_auth_token(client, "testuser_unauth", "testpass_unauth")
    # Try to create a post for a different user_id (e.g., 999 which doesn't belong to testuser_unauth)
    post_payload = {"title": "Unauthorized Post", "content": "This should fail."}
    response = client.post(f"/users/999/posts/", json=post_payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 # Forbidden
