from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.group import Group
from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate


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

    def create_group(self, group_in: GroupCreate) -> Group:
        group_data = group_in.model_dump()
        return self.repo.create_from_dict(group_data)

    def delete_group(self, group_id: int) -> None:
        group = self.repo.get(group_id)

        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        self.repo.delete(group)