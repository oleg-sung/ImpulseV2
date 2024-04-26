from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, Form, Body, Query
from starlette import status

from .dependencies import cheak_collection_id, cheak_club_name
from .schema.card import CardType, GetCard
from .schema.collection import (
    CreateNewCollection,
    ResponseCreateCollection,
    GetAllCollection,
    GetCollection,
    CollectionStatus,
)
from .services import CollectionService, CardService
from ..task.schema import CreateTask
from ..users.dependens import get_current_user
from ..users.schema.user import User

router = APIRouter(prefix="/collection", tags=["Collection"])


@router.get(
    "/",
    response_model=GetAllCollection,
    response_model_by_alias=True,
    response_model_exclude={"cards"},
    status_code=status.HTTP_200_OK,
)
async def get_all_collections(user: User = Depends(get_current_user)):
    data = await CollectionService(user.uid).get_all_collections_data()
    return data


@router.get(
    "/status/",
    response_model=list[GetCollection],
    response_model_by_alias=True,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_collection_by_status(
    status: CollectionStatus = Query(...), user: User = Depends(get_current_user)
):
    data = await CollectionService(user.uid).collection_by_status(status)
    return data


@router.get(
    "/{id_collection}/",
    response_model=GetCollection,
    response_model_by_alias=True,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_collection(id_collection: str, user: User = Depends(get_current_user)):
    data = await CollectionService(user.uid).get_collection_data(id_collection)
    return data


@router.post(
    "/create/",
    response_model=ResponseCreateCollection,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection(
    data: CreateNewCollection = Depends(cheak_club_name),
    user: User = Depends(get_current_user),
):
    """
    Create a new empty collection
    :return: JSON data
    """

    data = await CollectionService(user.uid).create_collection(data)
    return data


@router.patch(
    "/{id_collection}/change/status/",
    response_model=ResponseCreateCollection,
    status_code=status.HTTP_200_OK,
)
async def change_status(
    id_collection: str,
    status: CollectionStatus = Body(..., embed=True),
    user: User = Depends(get_current_user),
):
    """

    :param id_collection:
    :param status:
    :param user:
    :return:
    """
    data = await CollectionService(user.uid).change_status_collection(
        id_collection, status
    )
    return data


@router.post(
    "/{id_collection}/card/create/",
    response_model=CreateTask,
    status_code=status.HTTP_201_CREATED,
)
async def add_card_in_collection(
    file: UploadFile,
    type_: Annotated[CardType, Form()],
    name: Annotated[str, Form(max_length=20, min_length=2)],
    info: Annotated[str, Form(max_length=200)],
    position: Annotated[int, Form(le=44)],
    id_collection: str = Depends(cheak_collection_id),
    user: User = Depends(get_current_user),
):
    metadata = {"type": type_, "name": name, "info": info, "position": position}
    data = await CardService(id_collection, user.uid).create_card(file, metadata)
    return data


@router.get(
    "/{id_collection}/card/{id_card}/",
    response_model=GetCard,
    status_code=status.HTTP_200_OK,
)
async def get_card_from_collection(
    id_card: str,
    id_collection: str = Depends(cheak_collection_id),
    user: User = Depends(get_current_user),
):
    data = await CardService(id_collection, user.uid).get_card_info(id_card)
    return data


@router.get(
    "/{id_collection}/cards/",
    status_code=status.HTTP_200_OK,
)
async def get_cards(
    q: CardType = None,
    id_collection: str = Depends(cheak_collection_id),
    user: User = Depends(get_current_user),
):
    data = await CardService(id_collection, user.uid).get_cards_info(q)
    return data


@router.get("/{id_collection}/limit/")
async def get_limit_cards_in_collection(
    id_collection: str = Depends(cheak_collection_id),
    user: User = Depends(get_current_user),
):
    data = await CardService(id_collection, user.uid).get_limit()
    return data
