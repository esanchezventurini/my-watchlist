from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.group import Group


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


    def create_from_dict(self, data: dict) -> Group:
        group = Group(**data)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group


    def delete(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()