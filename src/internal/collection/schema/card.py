import uuid
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from internal.schema.image import Image


class CardType(str, Enum):
    """
    Enumeration of possible types of cards
    """

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


class Metadata(BaseModel):
    """Generic card schema"""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, exclude=True)
    collection: str
    type: CardType
    position: int
    name: str
    info: str

    def custom_dump(self):
        data = self.model_dump()
        data["id"] = self.id
        return data

    class Config:
        use_enum_values = True


class ImageCard(Image):
    metadata: Metadata


class GetCard(Metadata):
    id: str
    url: HttpUrl
