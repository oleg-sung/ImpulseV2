import datetime
from typing import Optional

from google.cloud.firestore_v1 import AsyncDocumentReference
from pydantic import EmailStr, BaseModel, Field, field_validator

from internal.schema.responce import BaseResponse
from internal.users.schema.user import UserType


class UserProfile(BaseModel):
    """
    General user profile for user admin type
    """

    user_type: UserType = Field(default=UserType.ADMIN, alias="userType")
    email: EmailStr
    first_name: str = Field(max_items=12, min_length=2, alias="firstName")
    middle_name: Optional[str] = Field(
        default=None, max_length=12, min_length=2, alias="middleName"
    )
    last_name: str = Field(max_length=20, min_length=2, alias="lastName")
    birthdate: datetime.datetime = Field(alias="birthdate")
    phone: str
    info: Optional[str] = None
    token: AsyncDocumentReference
    club_id: str = Field(alias="clubID")

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True


class GetUserProfile(BaseModel):
    user_type: UserType = Field(default=UserType.ADMIN, alias="userType")
    email: EmailStr
    first_name: str = Field(max_items=12, min_length=2, alias="firstName")
    middle_name: Optional[str] = Field(
        default=None, max_length=12, min_length=2, alias="middleName"
    )
    last_name: str = Field(max_length=20, min_length=2, alias="lastName")
    birth_date: str = Field(alias="birthdate")
    phone: str
    info: Optional[str] = None
    club_id: str = Field(alias="clubID")

    class Config:
        use_enum_values = True
        populate_by_name = True


class UpdateUserProfileSchema(BaseModel):
    first_name: Optional[str | None] = Field(None, alias="firstName")
    last_name: Optional[str | None] = Field(None, alias="lastName")
    middle_name: Optional[str | None] = Field(None, alias="middleName")
    birthdate: Optional[datetime.date | None] = Field(None, alias="birthdate")
    phone: Optional[str | None] = None
    info: Optional[str | None] = None

    @field_validator("first_name", "last_name", "middle_name")
    @classmethod
    def validate_name(cls, v: str):
        return v.capitalize()

    class Config:
        populate_by_name = True


class UpdateResponse(BaseResponse):
    id: str = Field(alias="userID")

    class Config:
        populate_by_name = True
