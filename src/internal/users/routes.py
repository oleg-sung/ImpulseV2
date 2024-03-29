from fastapi import APIRouter, Response, status, Depends, UploadFile

from internal.task.schema import CreateTask
from internal.users.dependens import get_current_user
from internal.users.schema.club import ClubInfo
from internal.users.schema.profile import (
    GetUserProfile,
    UpdateUserProfileSchema,
    UpdateResponse,
)
from internal.users.schema.user import UserCreate, UserLogin, User, UserCreateTast
from internal.users.services import UserServices, UserProfileService, ClubServices

router = APIRouter(
    prefix="/user",
    tags=["Users"],
)


@router.post(
    "/register/", response_model=UserCreateTast, status_code=status.HTTP_201_CREATED
)
async def user_register(user_data: UserCreate):
    """

    :param user_data:
    :return:
    """
    data = await UserServices().user_register(user_data)
    return data


@router.get(
    "/profile/",
    response_model=GetUserProfile,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
async def get_user_profile(user: User = Depends(get_current_user)):
    """

    :param user:
    :return:
    """
    data = await UserProfileService().get_user_profile(user.uid)
    return data


@router.post("/login/", status_code=status.HTTP_200_OK)
async def login(user: UserLogin, response: Response):
    """

    :param user:
    :param response:
    :return:
    """
    cookie = await UserServices().login_user(email=user.email, password=user.password)

    response.set_cookie(key="session", value=str(cookie))
    return {"message": "Cookie has been set"}


@router.post("/password/reset/", status_code=status.HTTP_201_CREATED)
async def change_password(user: User = Depends(get_current_user)):
    """
    Send password reset link to user's email_tools address
    :return: JSON with status
    """
    data = await UserServices().send_password_reset_link(user.email)
    return data


@router.put(
    "/profile/change/",
    response_model=UpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def change_profile_info(
    data: UpdateUserProfileSchema, user: User = Depends(get_current_user)
):
    data = await UserProfileService().update_user_profile(data, user.uid)
    return data


@router.get(
    "/club/",
    response_model=ClubInfo,
    response_model_by_alias=True,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def club_info(user: User = Depends(get_current_user)):
    data = await ClubServices().get_club_dict(user.uid)
    return data


@router.patch(
    "/club/change/", response_model=CreateTask, status_code=status.HTTP_200_OK
)
async def change_club_info(file: UploadFile, user: User = Depends(get_current_user)):
    data = await ClubServices().change_club_image(file, user.uid)
    return data


# @user_api.route('/club/coach/set/', methods=['POST'])
# @authorization
# def set_coach():
#     data = ClubServices().set_coach_to_club(request.json, request.user['user_id'])
#     return jsonify(data), 201
#
#
# @user_api.route('/club/coaches/', methods=['GET'])
# @authorization
# def list_coach():
#     ...
#
#
