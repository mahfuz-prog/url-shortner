from fastapi import APIRouter, status
from . import model
from . import service
from ..database.core import DbSession
from ..auth.service import current_user

router = APIRouter()


@router.get("/profile/", response_model=model.UserProfileResponse)
async def user_profile(current_user: current_user, db: DbSession):
    """
    service.get_user_by_id(db, current_user.get_uuid())
    return a user object

    model.UserProfileRequest extract and validate value from this user object
    """
    return service.get_user_by_id(db, current_user.get_uuid())


@router.put("/change-password/", status_code=status.HTTP_200_OK)
async def change_password(
    current_user: current_user, db: DbSession, user_request: model.ChangeUserPassword
):
    service.change_user_password(db, current_user.get_uuid(), user_request)


@router.put("/change-username/", status_code=status.HTTP_200_OK)
async def change_username(
    current_user: current_user, db: DbSession, user_request: model.ChangeUserName
):
    service.change_user_username(db, current_user.get_uuid(), user_request)
