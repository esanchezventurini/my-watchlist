from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.exceptions.group import NotGroupAdminException
from app.models.group import Group
from app.models.user import User
from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate, GroupUpdate, GroupRequestCreate


def _validate_group_admin(group: Group, user: User) -> None:
    user_group = next(
        (ug for ug in group.user_groups if ug.user_id == user.id),
        None
    )

    if not user_group or not user_group.admin:
        raise NotGroupAdminException()


def _validate_already_member(group: Group, user: User) -> None:
    if any(ug for ug in group.user_groups if ug.user_id == user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of the group")


def _validate_already_requested(group: Group, user: User) -> None:
    if any(ur for ur in group.requests if ur.requester_id == user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already requested to join the group")


class GroupService:
    def __init__(self, db: Session):
        self.repo = GroupRepository(db)

    def get_group(self, group_id: int) -> Group:
        group = self.repo.get(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group


    def list_groups(self, skip: int = 0, limit: int = 100) -> list[Group]:
        return self.repo.list(skip=skip, limit=limit)


    def create_group(self, group_in: GroupCreate, current_user: User) -> Group:
        group_data = group_in.model_dump()
        return self.repo.create_from_dict(group_data, current_user)


    def update_group(self, group_id: int, group_in: GroupUpdate, current_user: User) -> Group:
        group = self.get_group(group_id)
        _validate_group_admin(group, current_user)

        group_data = group_in.model_dump(exclude_unset=True)
        return self.repo.update_from_dict(group, group_data)


    def delete_group(self, group_id: int, current_user: User) -> None:
        group = self.get_group(group_id)
        _validate_group_admin(group, current_user)

        self.repo.delete(group)


    def request_to_join_group(self, group_id: int, group_request_in: GroupRequestCreate, current_user: User) -> None:
        group = self.get_group(group_id)

        _validate_already_member(group, current_user)

        if group.public:
            self.repo.add_to_group(group, current_user)
        else:
            _validate_already_requested(group, current_user)
            self.repo.create_group_request(group, current_user, group_request_in.reason)


    def join_group(self, group_id: int, current_user: User) -> None:
        group = self.get_group(group_id)

        _validate_already_member(group, current_user)

        if not group.public:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot join a private group without an approved request")

        self.repo.add_to_group(group, current_user)


    def approve_group_join_request(self, group_id: int, request_id: int, current_user: User) -> None:
        group = self.get_group(group_id)

        _validate_group_admin(group, current_user)

        group_request = next((r for r in group.requests if r.id == request_id), None)
        if not group_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group join request not found")

        self.repo.approve_group_request(group_request)