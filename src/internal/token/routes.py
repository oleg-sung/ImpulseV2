from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from internal.token.dependens import get_token
from internal.token.schema import BaseResponseToken, GetTokens, Token, UserDataByToken
from internal.token.services import TokenService
from internal.users.dependens import get_current_user
from internal.users.schema.user import User

router = APIRouter(prefix="/token", tags=["Token"])


@router.get(
    "/",
    response_model=List[GetTokens],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
async def get_all_user_token(user: User = Depends(get_current_user)):
    data = await TokenService().get_all_token_by_id(user.uid)
    return data


@router.get(
    "/{token_id}",
    response_model=Token,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
async def get_token_by_id(token: Token = Depends(get_token)):
    return token


@router.post(
    "/create/",
    response_model=BaseResponseToken,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_token_for_auth(user: User = Depends(get_current_user)):
    data = await TokenService().create_token(user.uid)
    return data


@router.patch(
    "/disable/{token_id}/",
    response_model=BaseResponseToken,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
async def disable_token_for_auth(token: Token = Depends(get_token)):
    data = await TokenService().disable_user_token(token)
    return data


@router.delete("/delete/{token_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token(token: Token = Depends(get_token)):
    data = await TokenService().delete_token_by_id(token)
    return data


@router.get("/coachs/", status_code=status.HTTP_200_OK)
async def get_coach(user: User = Depends(get_current_user)):
    data = await TokenService().get_coach_by_tokens(user.uid)
    return data


@router.get(
    "/users/",
    response_model=list[UserDataByToken],
    status_code=status.HTTP_200_OK,
)
async def get_users_by_token(token: Token = Depends(get_token)):
    data = await TokenService().get_detail_info_for_token(token.id)
    return data
