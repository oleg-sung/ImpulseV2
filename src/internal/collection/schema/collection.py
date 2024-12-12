import datetime
import uuid
from enum import Enum
from typing import Optional

from firebase_admin import firestore
from pydantic import BaseModel, Field, HttpUrl

from internal.schema.image import Image


class CollectionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    CLOSED = "closed"


class CollectionSize(str, Enum):
    """
    Enumeration of possible sizes of the collection
    """

    forty_cards = "fortyCards"
    sixty_cards = "sixtyCards"
    eighty_cards = "eightyCards"

    @staticmethod
    def get_size_dict(size: str) -> int:
        size_dict = {"fortyCards": 40, "sixtyCards": 60, "eightyCards": 80}
        return size_dict.get(size, None)

    @staticmethod
    def limit_cards() -> dict:
        return {
            "fortyCards": (25, 10, 4, 1),
            "sixtyCards": (38, 15, 6, 1),
            "eightyCards": (50, 20, 8, 2),
        }


class Collection(BaseModel):
    size: CollectionSize
    status: CollectionStatus
    name: str

    class Config:
        populate_by_name = True
        use_enum_values = True


class CardsDict(BaseModel):
    common: int
    uncommon: int
    rare: int
    legendary: int


class GeneralCollection(Collection):
    id: str
    amount_cards: CardsDict = Field(alias="amountCards")


class CreateNewCollection(BaseModel):
    size: CollectionSize = Field(default=CollectionSize.forty_cards)
    name: str = Field(min_length=2, max_length=60)
    description: Optional[str] = Field(None, alias="description")

    class Config:
        populate_by_name = True
        use_enum_values = True


class UpdateCollection(BaseModel):
    description: Optional[str] = Field(None, alias="description")
    cover: Optional[str] = Field(None, alias="cover")

    class Config:
        populate_by_name = True
        use_enum_values = True


class DataToCreateCollection(Collection):
    description: Optional[str] = Field(None, alias="description")
    status: CollectionStatus = Field(default=CollectionStatus.CREATED)
    cards: list = []
    date: datetime.datetime = Field(
        default=firestore.SERVER_TIMESTAMP, alias="date"
    )


class ResponseCreateCollection(BaseModel):
    status: bool
    id: str
    msg: str
    task_id: Optional[str] = Field(None, alias="taskId")


class GetAllCollection(BaseModel):
    collections: list[GeneralCollection]
    num: int


class GetCollection(Collection):
    id: str
    cards: list[str]
    date: datetime.datetime = Field(alias="date")
    description: Optional[str] = Field(default=None)
    amound_cards: CardsDict = Field(alias="amoundCards")
    cover: Optional[HttpUrl] = Field(None, alias="cover")

    class Config:
        use_enum_values = True
        populate_by_name = True


class GetCloseCollectionList(Collection):
    pass


class ChangeStatusCollection(Collection):
    status: CollectionStatus

    class Config:
        exclude = {"cards", "size", "name"}


class CoverCreate(Image):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, exclude=True)


class CollectionUpdate(BaseModel):
    cover: Optional[CoverCreate] = None
    description: Optional[str] = Field(None, alias="description")

    class Config:
        use_enum_values = True
        populate_by_name = True
