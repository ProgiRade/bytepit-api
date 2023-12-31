from typing import Annotated, List
from fastapi import APIRouter, Depends

from bytepit_api.services import admin_service

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.models.db_models import User
from bytepit_api.models.dtos import UserDTO
from bytepit_api.models.enums import Role


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/list-users", response_model=List[UserDTO])
def list_users(current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    return admin_service.get_users()


@router.get("/unapproved-organisers", response_model=List[UserDTO])
def list_unapproved_organisers(current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    return admin_service.get_unapproved_organisers()


@router.post("/confirm-organiser/{username}")
def confirm_organiser(username: str, current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    return admin_service.set_approved_organiser(username)


@router.post("/change-role/{username}/{new_role}")
def change_role(
    username: str,
    new_role: Annotated[Role, "new_role"],
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
):
    return admin_service.set_user_role(username, new_role)
