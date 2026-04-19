"""Integration tests for the /auth endpoints."""
import pytest
from tests.conftest import make_user


class TestLogin:
    def test_valid_credentials_return_token(self, client, db):
        user_name = "loginuser"
        password = "mypassword123"

        make_user(db, username=user_name, email="login@example.com", password=password)
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": user_name, "password": password},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client, db):
        user_name = "loginuser2"

        make_user(db, username=user_name, email="login2@example.com")
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": user_name, "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_unknown_user_returns_401(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            data={"username": "nobody", "password": "doesntmatter"},
        )
        assert resp.status_code == 401

    def test_missing_fields_returns_422(self, client):
        resp = client.post("/api/v1/auth/login", data={})
        assert resp.status_code == 422

