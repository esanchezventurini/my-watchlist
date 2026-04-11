"""Unit tests for UserService."""
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


def _mock_repo(
    username_exists=False,
    email_exists=False,
    user=None,
    users=None,
):
    """Return a mock UserRepository with sensible defaults."""
    repo = MagicMock()
    repo.username_exists.return_value = username_exists
    repo.email_exists.return_value = email_exists
    repo.get.return_value = user
    repo.get_by_username.return_value = user
    repo.list.return_value = users or []
    return repo


def _service_with_repo(repo):
    svc = UserService.__new__(UserService)
    svc.repo = repo
    return svc


# ── create_user ────────────────────────────────────────────────────────────────

class TestCreateUser:
    def test_happy_path(self):
        repo = _mock_repo()
        fake_user = MagicMock(id=1, username="alice")
        repo.create_from_dict.return_value = fake_user

        svc = _service_with_repo(repo)
        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            firstName="Alice",
            lastName="Smith",
            password="strongpassword",
        )
        result = svc.create_user(user_in)

        repo.create_from_dict.assert_called_once()
        call_data = repo.create_from_dict.call_args[0][0]
        assert "password" not in call_data
        assert "password_hash" in call_data
        assert result is fake_user

    def test_duplicate_username_raises_400(self):
        repo = _mock_repo(username_exists=True)
        svc = _service_with_repo(repo)
        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            firstName="Alice",
            lastName="Smith",
            password="strongpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            svc.create_user(user_in)
        assert exc_info.value.status_code == 400
        assert "Username already exists" in exc_info.value.detail

    def test_duplicate_email_raises_400(self):
        repo = _mock_repo(email_exists=True)
        svc = _service_with_repo(repo)
        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            firstName="Alice",
            lastName="Smith",
            password="strongpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            svc.create_user(user_in)
        assert exc_info.value.status_code == 400
        assert "Email already exists" in exc_info.value.detail

    def test_both_duplicate_returns_two_errors(self):
        repo = _mock_repo(username_exists=True, email_exists=True)
        svc = _service_with_repo(repo)
        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            firstName="Alice",
            lastName="Smith",
            password="strongpassword",
        )
        with pytest.raises(HTTPException) as exc_info:
            svc.create_user(user_in)
        assert len(exc_info.value.detail) == 2

    def test_password_is_hashed(self):
        repo = _mock_repo()
        repo.create_from_dict.return_value = MagicMock()
        svc = _service_with_repo(repo)
        user_in = UserCreate(
            username="alice",
            email="alice@example.com",
            firstName="Alice",
            lastName="Smith",
            password="plaintext",
        )
        svc.create_user(user_in)
        hashed = repo.create_from_dict.call_args[0][0]["password_hash"]
        assert hashed != "plaintext"
        assert len(hashed) > 20  # bcrypt hashes are long


# ── get_user ───────────────────────────────────────────────────────────────────

class TestGetUser:
    def test_returns_user_when_found(self):
        fake_user = MagicMock(id=1)
        repo = _mock_repo(user=fake_user)
        svc = _service_with_repo(repo)
        assert svc.get_user(1) is fake_user

    def test_raises_404_when_not_found(self):
        repo = _mock_repo(user=None)
        svc = _service_with_repo(repo)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_user(999)
        assert exc_info.value.status_code == 404


# ── list_users ─────────────────────────────────────────────────────────────────

class TestListUsers:
    def test_returns_list(self):
        users = [MagicMock(), MagicMock()]
        repo = _mock_repo(users=users)
        svc = _service_with_repo(repo)
        assert svc.list_users() == users
        repo.list.assert_called_once_with(skip=0, limit=100)

    def test_passes_pagination(self):
        repo = _mock_repo(users=[])
        svc = _service_with_repo(repo)
        svc.list_users(skip=10, limit=5)
        repo.list.assert_called_once_with(skip=10, limit=5)


# ── update_user ────────────────────────────────────────────────────────────────

class TestUpdateUser:
    def test_happy_path(self):
        fake_user = MagicMock(id=1)
        repo = _mock_repo(user=fake_user)
        repo.update.return_value = fake_user
        svc = _service_with_repo(repo)

        user_in = UserUpdate(email="new@example.com")
        result = svc.update_user(1, user_in)
        repo.update.assert_called_once_with(fake_user, user_in)
        assert result is fake_user

    def test_raises_404_when_not_found(self):
        repo = _mock_repo(user=None)
        svc = _service_with_repo(repo)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_user(999, UserUpdate())
        assert exc_info.value.status_code == 404


# ── delete_user ────────────────────────────────────────────────────────────────

class TestDeleteUser:
    def test_happy_path(self):
        fake_user = MagicMock(id=1)
        repo = _mock_repo(user=fake_user)
        svc = _service_with_repo(repo)
        svc.delete_user(1)
        repo.delete.assert_called_once_with(fake_user)

    def test_raises_404_when_not_found(self):
        repo = _mock_repo(user=None)
        svc = _service_with_repo(repo)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_user(999)
        assert exc_info.value.status_code == 404


# ── authenticate_user ──────────────────────────────────────────────────────────

class TestAuthenticateUser:
    def test_happy_path(self):
        from app.core.security import hash_password

        fake_user = MagicMock()
        fake_user.password_hash = hash_password("correct_password")
        repo = _mock_repo(user=fake_user)
        svc = _service_with_repo(repo)

        result = svc.authenticate_user("alice", "correct_password")
        assert result is fake_user

    def test_wrong_password_raises_401(self):
        from app.core.security import hash_password

        fake_user = MagicMock()
        fake_user.password_hash = hash_password("correct_password")
        repo = _mock_repo(user=fake_user)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.authenticate_user("alice", "wrongpassword")
        assert exc_info.value.status_code == 401

    def test_unknown_user_raises_401(self):
        repo = _mock_repo(user=None)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.authenticate_user("nobody", "password")
        assert exc_info.value.status_code == 401

