import uuid
from typing import Optional

from pydantic import Field, BaseModel, AnyHttpUrl

from internal.schema.image import Image


class CreateClub(BaseModel):
    club_name: str = Field(alias="name")

    class Config:
        populate_by_name = True


class UpdateClubSchema(BaseModel):
    motto: str = Field(min_length=5, max_length=300)


class ClubInfo(BaseModel):
    club_name: str = Field(alias="name")
    motto: Optional[str] = None
    image: Optional[AnyHttpUrl] = None


class ChangeClubImage(Image):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
