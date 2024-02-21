import datetime
from enum import Enum

from firebase_admin import firestore
from pydantic import BaseModel, Field, model_validator


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


class Collection(BaseModel):
    size: CollectionSize
    is_active: bool = Field(alias="isActive")
    name: str

    class Config:
        populate_by_name = True
        use_enum_values = True


class GeneralCollection(Collection):
    id: str


class CreateCollection(Collection):
    size: CollectionSize = CollectionSize.forty_cards
    cards: list = []
    is_active: bool = Field(default=True, alias="isActive")
    name: str = Field(min_length=2, max_length=40)
    crated_at: datetime.datetime = Field(
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


class DisableCollection(Collection):
    is_active: bool = Field(alias="isActive")

    @model_validator(mode="after")
    def disable(self):
        self.is_active = False if self.is_active else True
        return self

    class Config:
        exclude = {"cards", "size", "name"}
