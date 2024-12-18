import datetime
import re
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
    first_name: str = Field(max_items=20, min_length=2, alias="firstName")
    last_name: str = Field(max_length=20, min_length=2, alias="lastName")
    birthday: datetime.datetime = Field(alias="birthday")
    token: str = Field(default="")
    club_id: str = Field(alias="clubID")

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True


class GetUserProfile(BaseModel):
    id: str = Field(..., examples=["RsZnqWPUXYZnkNAEMT11"])
    user_type: UserType = Field(default=UserType.ADMIN, alias="userType")
    email: EmailStr
    first_name: str = Field(max_items=20, min_length=2, alias="firstName")
    middle_name: Optional[str] = Field(
        default=None, max_length=20, min_length=2, alias="middleName"
    )
    last_name: str = Field(max_length=20, min_length=2, alias="lastName")
    birthday: datetime.date = Field(alias="birthday")
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
    birthday: Optional[datetime.date | None] = Field(None, alias="birthday")
    phone: Optional[str | None] = None
    info: Optional[str | None] = None

    @field_validator("birthday")
    @classmethod
    def age_must_be_at_least_five(cls, v):
        if v is None:
            return v

        today = datetime.date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 5:
            raise ValueError("Age must be at least 5 years")

        return v

    @field_validator("first_name", "last_name", "middle_name")
    @classmethod
    def validate_name(cls, v: str):
        if v:
            if not cls.contains_only_letters_and_spaces(v):
                raise ValueError('Value has to be a string')
            return v.capitalize()
        else:
            return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v:
            result = re.match(
                r'^[78]?\d{10}$', v
            )
            if not bool(result):
                raise ValueError('Incorrect phone format')
        return v

    @staticmethod
    def contains_only_letters_and_spaces(string: str):
        return all(char.isalpha() or char.isspace() for char in string)

    class Config:
        populate_by_name = True


class UpdateResponse(BaseResponse):
    id: str = Field(alias="userID")

    class Config:
        populate_by_name = True
