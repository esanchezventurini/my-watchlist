"""Unit tests for GroupService."""
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from app.exceptions.group import NotGroupAdminException
from app.schemas.group import GroupCreate, GroupUpdate, GroupRequestCreate
from app.services.group_service import GroupService


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_user_group(user_id, admin=False):
    ug = MagicMock()
    ug.user_id = user_id
    ug.admin = admin
    return ug


def _make_group_request(requester_id, request_id=1):
    gr = MagicMock()
    gr.id = request_id
    gr.requester_id = requester_id
    return gr


def _make_group(public=True, user_groups=None, requests=None):
    group = MagicMock()
    group.public = public
    group.user_groups = user_groups or []
    group.requests = requests or []
    return group


def _mock_repo(group=None, groups=None):
    repo = MagicMock()
    repo.get.return_value = group
    repo.list.return_value = groups or []
    return repo


def _service_with_repo(repo):
    svc = GroupService.__new__(GroupService)
    svc.repo = repo
    return svc


# ── get_group ──────────────────────────────────────────────────────────────────

class TestGetGroup:
    def test_returns_group(self):
        group = _make_group()
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)
        assert svc.get_group(1) is group

    def test_raises_404_when_not_found(self):
        repo = _mock_repo(group=None)
        svc = _service_with_repo(repo)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_group(99)
        assert exc_info.value.status_code == 404


# ── list_groups ────────────────────────────────────────────────────────────────

class TestListGroups:
    def test_returns_list(self):
        groups = [_make_group(), _make_group()]
        repo = _mock_repo(groups=groups)
        svc = _service_with_repo(repo)
        assert svc.list_groups() == groups

    def test_passes_pagination(self):
        repo = _mock_repo(groups=[])
        svc = _service_with_repo(repo)
        svc.list_groups(skip=5, limit=10)
        repo.list.assert_called_once_with(skip=5, limit=10)


# ── create_group ───────────────────────────────────────────────────────────────

class TestCreateGroup:
    def test_calls_repo_with_data_and_user(self):
        fake_group = _make_group()
        repo = _mock_repo()
        repo.create_from_dict.return_value = fake_group
        svc = _service_with_repo(repo)

        user = MagicMock(id=1)
        group_in = GroupCreate(name="My Group", description="Desc", public=True)
        result = svc.create_group(group_in, user)

        repo.create_from_dict.assert_called_once()
        assert result is fake_group


# ── update_group ───────────────────────────────────────────────────────────────

class TestUpdateGroup:
    def test_admin_can_update(self):
        user = MagicMock(id=1)
        ug = _make_user_group(user_id=1, admin=True)
        group = _make_group(user_groups=[ug])
        repo = _mock_repo(group=group)
        repo.update_from_dict.return_value = group
        svc = _service_with_repo(repo)

        group_in = GroupUpdate(name="New Name", description="New Desc", public=False)
        result = svc.update_group(1, group_in, user)

        repo.update_from_dict.assert_called_once()
        assert result is group

    def test_non_admin_raises_403(self):
        user = MagicMock(id=2)
        ug = _make_user_group(user_id=2, admin=False)
        group = _make_group(user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        group_in = GroupUpdate(name="Name", description="Desc", public=True)
        with pytest.raises(NotGroupAdminException):
            svc.update_group(1, group_in, user)

    def test_non_member_raises_403(self):
        user = MagicMock(id=99)
        group = _make_group(user_groups=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(NotGroupAdminException):
            svc.update_group(1, GroupUpdate(name="N", description="D", public=True), user)


# ── delete_group ───────────────────────────────────────────────────────────────

class TestDeleteGroup:
    def test_admin_can_delete(self):
        user = MagicMock(id=1)
        ug = _make_user_group(user_id=1, admin=True)
        group = _make_group(user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        svc.delete_group(1, user)
        repo.delete.assert_called_once_with(group)

    def test_non_admin_raises_403(self):
        user = MagicMock(id=2)
        ug = _make_user_group(user_id=2, admin=False)
        group = _make_group(user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(NotGroupAdminException):
            svc.delete_group(1, user)


# ── request_to_join_group ──────────────────────────────────────────────────────

class TestRequestToJoinGroup:
    def test_public_group_adds_directly(self):
        user = MagicMock(id=5)
        group = _make_group(public=True, user_groups=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        svc.request_to_join_group(1, GroupRequestCreate(reason="Please"), user)
        repo.add_to_group.assert_called_once_with(group, user)
        repo.create_group_request.assert_not_called()

    def test_private_group_creates_request(self):
        user = MagicMock(id=5)
        group = _make_group(public=False, user_groups=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        svc.request_to_join_group(1, GroupRequestCreate(reason="Please let me in"), user)
        repo.create_group_request.assert_called_once_with(group, user, "Please let me in")

    def test_already_member_raises_400(self):
        user = MagicMock(id=5)
        ug = _make_user_group(user_id=5)
        group = _make_group(public=True, user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.request_to_join_group(1, GroupRequestCreate(reason="Hi"), user)
        assert exc_info.value.status_code == 400

    def test_already_requested_private_group_raises_400(self):
        user = MagicMock(id=5)
        gr = _make_group_request(requester_id=5)
        group = _make_group(public=False, user_groups=[], requests=[gr])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.request_to_join_group(1, GroupRequestCreate(reason="Please"), user)
        assert exc_info.value.status_code == 400


# ── join_group ─────────────────────────────────────────────────────────────────

class TestJoinGroup:
    def test_public_group_joins(self):
        user = MagicMock(id=5)
        group = _make_group(public=True, user_groups=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        svc.join_group(1, user)
        repo.add_to_group.assert_called_once_with(group, user)

    def test_private_group_raises_403(self):
        user = MagicMock(id=5)
        group = _make_group(public=False, user_groups=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.join_group(1, user)
        assert exc_info.value.status_code == 403

    def test_already_member_raises_400(self):
        user = MagicMock(id=5)
        ug = _make_user_group(user_id=5)
        group = _make_group(public=True, user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.join_group(1, user)
        assert exc_info.value.status_code == 400


# ── approve_group_join_request ─────────────────────────────────────────────────

class TestApproveGroupJoinRequest:
    def test_admin_can_approve(self):
        user = MagicMock(id=1)
        ug = _make_user_group(user_id=1, admin=True)
        gr = _make_group_request(requester_id=5, request_id=10)
        group = _make_group(user_groups=[ug], requests=[gr])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        svc.approve_group_join_request(1, 10, user)
        repo.approve_group_request.assert_called_once_with(gr)

    def test_non_admin_raises_403(self):
        user = MagicMock(id=2)
        ug = _make_user_group(user_id=2, admin=False)
        group = _make_group(user_groups=[ug])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(NotGroupAdminException):
            svc.approve_group_join_request(1, 10, user)

    def test_missing_request_raises_404(self):
        user = MagicMock(id=1)
        ug = _make_user_group(user_id=1, admin=True)
        group = _make_group(user_groups=[ug], requests=[])
        repo = _mock_repo(group=group)
        svc = _service_with_repo(repo)

        with pytest.raises(HTTPException) as exc_info:
            svc.approve_group_join_request(1, 999, user)
        assert exc_info.value.status_code == 404

