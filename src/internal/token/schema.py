import datetime
import uuid

from firebase_admin import firestore
from pydantic import BaseModel, Field, model_validator

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
    created_at: datetime.datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CreateToken(BaseToken):
    is_active: bool = Field(default=True, alias="isActive")
    auth_count: int = Field(default=0, alias="authCount")
    owner_type: UserType = Field(default=UserType.ADMIN, alias="userType")
    code: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime.datetime = Field(
        default=firestore.SERVER_TIMESTAMP, alias="createdAt"
    )


class Token(BaseToken):
    id: str


class GetTokens(BaseModel):
    id: str = Field(examples=["xqPi3BHItfQS8lfsUX0S"])
    is_active: bool = Field(alias="isActive")

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
