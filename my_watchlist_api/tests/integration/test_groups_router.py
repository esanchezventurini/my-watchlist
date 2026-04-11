"""Integration tests for the /groups endpoints."""
import pytest
from tests.conftest import make_user, make_group, auth_headers


class TestListGroups:
    def test_returns_200(self, client):
        resp = client.get("/api/v1/groups/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetGroup:
    def test_returns_group(self, client, db):
        user = make_user(db, username="grpowner", email="grpowner@example.com")
        group = make_group(db, creator=user, name="My Group")
        resp = client.get(f"/api/v1/groups/{group.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "My Group"

    def test_unknown_id_returns_404(self, client):
        resp = client.get("/api/v1/groups/999999")
        assert resp.status_code == 404


class TestCreateGroup:
    def test_authenticated_user_can_create(self, client, db):
        make_user(db, username="creator", email="creator@example.com")
        headers = auth_headers(client, "creator", "secret123")
        resp = client.post("/api/v1/groups/", json={
            "name": "New Group",
            "description": "A brand new group",
            "public": True,
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Group"

    def test_unauthenticated_returns_401(self, client):
        resp = client.post("/api/v1/groups/", json={
            "name": "New Group",
            "description": "Desc",
            "public": True,
        })
        assert resp.status_code == 401


class TestUpdateGroup:
    def test_admin_can_update(self, client, db):
        user = make_user(db, username="updater", email="updater@example.com")
        group = make_group(db, creator=user, name="Old Name")
        headers = auth_headers(client, "updater", "secret123")
        resp = client.patch(f"/api/v1/groups/{group.id}", json={
            "name": "New Name",
            "description": "New Desc",
            "public": False,
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_non_admin_cannot_update(self, client, db):
        owner = make_user(db, username="ownrr", email="ownrr@example.com")
        non_admin_member = make_user(db, username="updater", email="updater@example.com")
        group = make_group(db, creator=owner, name="Old Name", other_members=[non_admin_member])
        headers = auth_headers(client, "updater", "secret123")
        resp = client.patch(f"/api/v1/groups/{group.id}", json={
            "name": "New Name",
            "description": "New Desc",
            "public": False,
        }, headers=headers)
        assert resp.status_code == 403
        assert resp.json()["detail"] == "You must be a group admin to perform this action"

    def test_non_member_cannot_update(self, client, db):
        owner = make_user(db, username="ownrr", email="ownrr@example.com")
        group = make_group(db, creator=owner, name="Protected")
        make_user(db, username="intruder", email="intruder@example.com")
        headers = auth_headers(client, "intruder", "secret123")
        resp = client.patch(f"/api/v1/groups/{group.id}", json={
            "name": "Hacked",
            "description": "Desc",
            "public": True,
        }, headers=headers)
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, client, db):
        user = make_user(db, username="noauth_upd", email="noauth_upd@example.com")
        group = make_group(db, creator=user)
        resp = client.patch(f"/api/v1/groups/{group.id}", json={
            "name": "X",
            "description": "Y",
            "public": True,
        })
        assert resp.status_code == 401


class TestDeleteGroup:
    def test_admin_can_delete(self, client, db):
        user = make_user(db, username="deleter", email="deleter@example.com")
        group = make_group(db, creator=user, name="ToDelete")
        headers = auth_headers(client, "deleter", "secret123")
        resp = client.delete(f"/api/v1/groups/{group.id}", headers=headers)
        assert resp.status_code == 200

    def test_non_admin_cannot_delete(self, client, db):
        owner = make_user(db, username="del_owner", email="del_owner@example.com")
        group = make_group(db, creator=owner)
        make_user(db, username="del_other", email="del_other@example.com")
        headers = auth_headers(client, "del_other", "secret123")
        resp = client.delete(f"/api/v1/groups/{group.id}", headers=headers)
        assert resp.status_code == 403


class TestJoinGroup:
    def test_user_can_join_public_group(self, client, db):
        owner = make_user(db, username="join_owner", email="join_owner@example.com")
        group = make_group(db, creator=owner, public=True)
        make_user(db, username="joiner", email="joiner@example.com")
        headers = auth_headers(client, "joiner", "secret123")
        resp = client.post(f"/api/v1/groups/{group.id}/members", headers=headers)
        assert resp.status_code == 200

    def test_user_cannot_join_private_group_directly(self, client, db):
        owner = make_user(db, username="pvt_owner", email="pvt_owner@example.com")
        group = make_group(db, creator=owner, public=False)
        make_user(db, username="pvt_joiner", email="pvt_joiner@example.com")
        headers = auth_headers(client, "pvt_joiner", "secret123")
        resp = client.post(f"/api/v1/groups/{group.id}/members", headers=headers)
        assert resp.status_code == 403

    def test_cannot_join_twice(self, client, db):
        owner = make_user(db, username="twice_owner", email="twice_owner@example.com")
        group = make_group(db, creator=owner, public=True)
        headers = auth_headers(client, "twice_owner", "secret123")
        resp = client.post(f"/api/v1/groups/{group.id}/members", headers=headers)
        assert resp.status_code == 400  # already a member


class TestRequestToJoinGroup:
    def test_can_request_private_group(self, client, db):
        owner = make_user(db, username="req_owner", email="req_owner@example.com")
        group = make_group(db, creator=owner, public=False)
        make_user(db, username="requester", email="requester@example.com")
        headers = auth_headers(client, "requester", "secret123")
        resp = client.post(f"/api/v1/groups/{group.id}/requests", json={"reason": "Please"}, headers=headers)
        assert resp.status_code == 200

    def test_cannot_request_twice(self, client, db):
        owner = make_user(db, username="req2_owner", email="req2_owner@example.com")
        group = make_group(db, creator=owner, public=False)
        make_user(db, username="requester2", email="requester2@example.com")
        headers = auth_headers(client, "requester2", "secret123")
        # First request
        client.post(f"/api/v1/groups/{group.id}/requests", json={"reason": "Please"}, headers=headers)
        # Second request
        resp = client.post(f"/api/v1/groups/{group.id}/requests", json={"reason": "Please again"}, headers=headers)
        assert resp.status_code == 400


class TestApproveRequest:
    def test_admin_can_approve(self, client, db):
        owner = make_user(db, username="appr_owner", email="appr_owner@example.com")
        group = make_group(db, creator=owner, public=False)
        make_user(db, username="appr_req", email="appr_req@example.com")
        req_headers = auth_headers(client, "appr_req", "secret123")
        # Create request
        client.post(f"/api/v1/groups/{group.id}/requests", json={"reason": "Hi"}, headers=req_headers)

        # Fetch request id
        from app.models.group_request import GroupRequest
        from sqlalchemy import select
        stmt = select(GroupRequest).where(GroupRequest.group_id == group.id)
        group_request = db.execute(stmt).scalar_one()

        owner_headers = auth_headers(client, "appr_owner", "secret123")
        resp = client.post(f"/api/v1/groups/{group.id}/requests/{group_request.id}/approve", headers=owner_headers)
        assert resp.status_code == 200

    def test_non_admin_cannot_approve(self, client, db):
        owner = make_user(db, username="nappr_owner", email="nappr_owner@example.com")
        group = make_group(db, creator=owner, public=False)
        make_user(db, username="nappr_req", email="nappr_req@example.com")
        req_headers = auth_headers(client, "nappr_req", "secret123")
        client.post(f"/api/v1/groups/{group.id}/requests", json={"reason": "Hi"}, headers=req_headers)

        from app.models.group_request import GroupRequest
        from sqlalchemy import select
        stmt = select(GroupRequest).where(GroupRequest.group_id == group.id)
        group_request = db.execute(stmt).scalar_one()

        resp = client.post(
            f"/api/v1/groups/{group.id}/requests/{group_request.id}/approve",
            headers=req_headers,  # requester tries to approve their own request
        )
        assert resp.status_code == 403

