"""Unit tests for security helpers."""
import pytest
import jwt
from datetime import datetime, timezone, timedelta

from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


class TestHashPassword:
    def test_returns_string(self):
        assert isinstance(hash_password("mypassword"), str)

    def test_different_calls_produce_different_hashes(self):
        h1 = hash_password("mypassword")
        h2 = hash_password("mypassword")
        # bcrypt uses random salts
        assert h1 != h2

    def test_long_password_does_not_raise(self):
        long_pw = "a" * 200
        result = hash_password(long_pw)
        assert isinstance(result, str)


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_long_password_verifies_correctly(self):
        long_pw = "b" * 200
        hashed = hash_password(long_pw)
        assert verify_password(long_pw, hashed) is True
        assert verify_password("b" * 199, hashed) is False


class TestCreateAccessToken:
    def test_returns_decodable_jwt(self):
        token = create_access_token(user_id=42)
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "42"

    def test_token_contains_expiry(self):
        token = create_access_token(user_id=1)
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert "exp" in payload

    def test_expired_token_raises(self):
        # Manually craft an already-expired token
        payload = {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        expired_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

