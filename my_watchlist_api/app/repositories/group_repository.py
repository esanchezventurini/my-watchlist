from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums.group_request_status import GroupRequestStatus
from app.models.group import Group
from app.models.group_request import GroupRequest
from app.models.user import User
from app.models.user_group import UserGroup


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, group_id: int) -> Group | None:
        return (
            self.db.query(Group)
            .options(selectinload(Group.watchlists))
            .options(selectinload(Group.users))
            .options(selectinload(Group.user_groups))
            .filter(Group.id == group_id)
            .first()
        )


    def list(self, skip: int = 0, limit: int = 100) -> list[Group]:
        stmt = select(Group).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())


    def create_from_dict(self, data: dict, creator: User) -> Group:
        group = Group(**data)

        user_group = UserGroup(
            user=creator,
            admin=1
        )
        group.user_groups.append(user_group)

        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        return group


    def update_from_dict(self, group: Group, data: dict) -> Group:
        for key, value in data.items():
            setattr(group, key, value)

        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        return group


    def delete(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()


    def add_to_group(self, group: Group, requester: User) -> None:
        user_group = UserGroup(
            user=requester,
            group=group,
            admin=0
        )
        self.db.add(user_group)
        self.db.commit()


    def create_group_request(self, group: Group, requester: User, reason: str | None) -> GroupRequest:
        group_request = GroupRequest(
            user=requester,
            group=group,
            reason=reason
        )
        self.db.add(group_request)
        self.db.commit()
        self.db.refresh(group_request)

        return group_request


    def approve_group_request(self, group_request: GroupRequest) -> None:
        group_request.status = GroupRequestStatus.APPROVED

        user_group = UserGroup(
            user=group_request.user,
            group=group_request.group,
            admin=0
        )

        self.db.add(user_group)
        self.db.commit()
