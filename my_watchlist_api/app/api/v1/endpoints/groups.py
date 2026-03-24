from fastapi import APIRouter, Depends, Query

from app.dependencies import get_group_service
from app.schemas.group import GroupRead

router = APIRouter(prefix="/groups", tags=["users"])


@router.get("/", response_model=list[GroupRead])
def list_groups(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    group_service = Depends(get_group_service)
):
    return group_service.list_groups(skip=skip, limit=limit)


@router.get("/{group_id}", response_model=GroupRead)
def get_group_by_id(group_id: int, group_service = Depends(get_group_service)):
    return group_service.get_group(group_id)
