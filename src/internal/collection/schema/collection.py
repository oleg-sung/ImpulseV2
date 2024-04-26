import datetime
from enum import Enum
from typing import Optional

from firebase_admin import firestore
from pydantic import BaseModel, Field


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


class GeneralCollection(Collection):
    id: str


class CreateNewCollection(BaseModel):
    size: CollectionSize = Field(default=CollectionSize.forty_cards)
    name: str = Field(min_length=2, max_length=60)

    class Config:
        populate_by_name = True
        use_enum_values = True


class DataToCreateCollection(Collection):
    status: CollectionStatus = Field(default=CollectionStatus.CREATED)
    cards: list = []
    date: datetime.datetime = Field(
        default=firestore.SERVER_TIMESTAMP, alias="createdAt"
    )


class ResponseCreateCollection(BaseModel):
    status: bool
    id: str


class GetAllCollection(BaseModel):
    collections: list[GeneralCollection]
    num: int


class GetCollection(Collection):
    id: str
    cards: list[str]
    created_at: datetime.datetime = Field(alias="createdAt")
    motto: Optional[str] = Field(default=None)


class ChangeStatusCollection(Collection):
    status: CollectionStatus

    class Config:
        exclude = {"cards", "size", "name"}
