from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.dependencies import get_group_service
from app.schemas.group import GroupRead, GroupCreate, GroupUpdate

router = APIRouter(prefix="/groups", tags=["groups"])


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


@router.post("/", response_model=GroupRead)
def create_group(group_in: GroupCreate,
                 group_service = Depends(get_group_service),
                 current_user = Depends(get_current_user)):
    return group_service.create_group(group_in, current_user)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(group_id: int,
                 group_in: GroupUpdate,
                 group_service = Depends(get_group_service),
                 current_user = Depends(get_current_user)):
    return group_service.update_group(group_id, group_in, current_user)


@router.delete("/{group_id}")
def delete_group(group_id: int,
                 group_service = Depends(get_group_service),
                 current_user = Depends(get_current_user)):
    return group_service.delete_group(group_id, current_user)