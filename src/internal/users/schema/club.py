import uuid
from typing import Optional

from pydantic import Field, BaseModel, AnyHttpUrl

from internal.schema.image import Image


class CreateClub(BaseModel):
    club_name: str = Field(alias="name", min_length=2, max_length=60)

    class Config:
        populate_by_name = True


class UpdateClubSchema(BaseModel):
    motto: str = Field(min_length=5, max_length=300)


class ClubInfo(BaseModel):
    club_name: str = Field(alias="name", min_length=2, max_length=60)
    motto: Optional[str] = Field(default=None, max_length=300)
    image: Optional[AnyHttpUrl] = None

    class Config:
        populate_by_name = True


class ClubImage(Image):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
