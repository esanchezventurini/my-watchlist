"""Integration tests for the /users endpoints."""
import pytest
from tests.conftest import make_user, auth_headers


class TestCreateUser:
    def test_creates_user_successfully(self, client):
        resp = client.post("/api/v1/users/", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "firstName": "New",
            "lastName": "User",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert "password_hash" not in data
        assert "id" in data

    def test_duplicate_username_returns_400(self, client, db):
        make_user(db, username="dupeuser", email="dupe@example.com")
        resp = client.post("/api/v1/users/", json={
            "username": "dupeuser",
            "email": "other@example.com",
            "firstName": "Dupe",
            "lastName": "User",
            "password": "password123",
        })
        assert resp.status_code == 400

    def test_duplicate_email_returns_400(self, client, db):
        make_user(db, username="emailuser", email="shared@example.com")
        resp = client.post("/api/v1/users/", json={
            "username": "otherusername",
            "email": "shared@example.com",
            "firstName": "Other",
            "lastName": "User",
            "password": "password123",
        })
        assert resp.status_code == 400

    def test_invalid_email_returns_422(self, client):
        resp = client.post("/api/v1/users/", json={
            "username": "baduser",
            "email": "not-an-email",
            "firstName": "Bad",
            "lastName": "User",
            "password": "password123",
        })
        assert resp.status_code == 422


class TestListUsers:
    def test_returns_200(self, client):
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_pagination_params(self, client):
        resp = client.get("/api/v1/users/?skip=0&limit=5")
        assert resp.status_code == 200

    def test_invalid_limit_returns_422(self, client):
        resp = client.get("/api/v1/users/?limit=0")
        assert resp.status_code == 422


class TestGetMe:
    def test_returns_current_user(self, client, db):
        make_user(db, username="meuser", email="me@example.com")
        headers = auth_headers(client, "meuser", "secret123")
        resp = client.get("/api/v1/users/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "meuser"

    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401


class TestUpdateMe:
    def test_updates_email(self, client, db):
        make_user(db, username="updateuser", email="update@example.com")
        headers = auth_headers(client, "updateuser", "secret123")
        resp = client.patch("/api/v1/users/me", json={"email": "updated@example.com"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "updated@example.com"

    def test_unauthenticated_returns_401(self, client):
        resp = client.patch("/api/v1/users/me", json={"email": "x@x.com"})
        assert resp.status_code == 401


class TestDeleteMe:
    def test_deletes_current_user(self, client, db):
        make_user(db, username="deleteuser", email="delete@example.com")
        headers = auth_headers(client, "deleteuser", "secret123")
        resp = client.delete("/api/v1/users/me", headers=headers)
        assert resp.status_code == 204

    def test_unauthenticated_returns_401(self, client):
        resp = client.delete("/api/v1/users/me")
        assert resp.status_code == 401


class TestCombinedUsers:
    def test_create_and_get_user(self, client):
        username = "combineduser"
        email = "newuser@example.com"
        first_name = "Combined"
        last_name = "User"

        create_resp = client.post("/api/v1/users/", json={
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "password": "password123",
        })
        assert create_resp.status_code == 201
        create_data = create_resp.json()

        get_resp = client.get("/api/v1/users/")
        assert get_resp.status_code == 200

        get_data = get_resp.json()

        user = next((u for u in get_data if u["id"] == create_data["id"]), None)
        assert user is not None
        assert user["username"] == username
        assert user["firstName"] == first_name
        assert user["lastName"] == last_name
