import datetime
import uuid
from typing import Optional

from firebase_admin import firestore
from pydantic import BaseModel, Field, model_validator, HttpUrl

from internal.users.schema.user import UserType


class BaseResponseToken(BaseModel):
    token_id: str = Field(examples=["xqPi3BHItfQS8lfsUX0S"], alias="tokenId")

    class Config:
        populate_by_name = True


class BaseToken(BaseModel):
    code: str
    auth_count: int = Field(alias="authCount")
    club_id: str = Field(alias="clubID")
    is_active: bool = Field(alias="isActive")
    owner_id: str = Field(alias="userCreatedID")
    owner_type: UserType = Field(alias="userType")
    date: datetime.datetime = Field(alias="date")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CreateToken(BaseToken):
    is_active: bool = Field(default=True, alias="isActive")
    auth_count: int = Field(default=0, alias="authCount")
    owner_type: UserType = Field(default=UserType.COACH, alias="userType")
    code: str = Field(default_factory=lambda: uuid.uuid4().hex)
    date: datetime.datetime = Field(
        default=firestore.SERVER_TIMESTAMP, alias="date"
    )


class Token(BaseToken):
    id: str


class GetTokens(BaseModel):
    id: str = Field(examples=["xqPi3BHItfQS8lfsUX0S"])
    is_active: bool = Field(alias="isActive")
    code: str
    auth_count: int = Field(alias="authCount")
    created_at: datetime.datetime = Field(alias="date")

    class Config:
        populate_by_name = True


class DisableToken(BaseModel):
    is_active: bool = Field(alias="isActive")

    @model_validator(mode="after")
    def validate_is_active(self):
        self.is_active = True if self.is_active is False else False
        return self

    class Config:
        populate_by_name = True


class UserDataByToken(BaseModel):
    id: str
    first_name: str = Field(alias="firstName")
    middle_name: Optional[str | None] = Field(default=None, alias="middleName")
    last_name: str = Field(alias="lastName")
    image: Optional[HttpUrl | None] = Field(default=None)

    class Config:
        populate_by_name = True
