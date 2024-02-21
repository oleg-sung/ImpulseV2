import datetime
from typing import Optional

from fastapi import HTTPException
from google.cloud.firestore_v1 import DocumentReference
from pydantic import EmailStr, BaseModel, model_validator, Field, field_validator
from starlette import status

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
    birth_date: datetime.date = Field(alias="birthdate")
    phone: str
    info: Optional[str] = None
    token: DocumentReference
    club_id: str = Field(alias="clubID")

    @model_validator(mode="after")
    def validate_birthdate(self):
        self.birthdate = self.birthdate.strftime("%d-%m-%Y")
        return self

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
    birth_date: Optional[str | None] = Field(None, alias="birthdate")
    phone: Optional[str | None] = None
    info: Optional[str | None] = None

    @classmethod
    @field_validator("birth_date")
    def validate_birthday(cls, v):
        if v:
            try:
                datetime.datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="birth day must be in format YYYY-MM-DD",
                )
        return v

    class Config:
        populate_by_name = True


class UpdateResponse(BaseModel):
    status: bool
    message: str
    id: str = Field(alias="userID")

    class Config:
        populate_by_name = True
