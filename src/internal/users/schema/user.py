import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator

from internal.schema.responce import BaseResponse


class UserType(str, Enum):
    """
    Enumeration of possible user
    """

    PLAYER = "player"
    COACH = "coach"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(min_length=2, max_length=20, alias="firstName")
    last_name: str = Field(min_length=2, max_length=20, alias="lastName")
    birthdate: datetime.date
    club_name: str = Field(min_length=2, max_length=20, alias="name")

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def password_complexity(self):
        # pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!#%?&]+$"
        result = len(self.password)
        if 6 > result or result > 8:
            raise ValueError("Password must be between 6 and 8 characters")
        return self

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str):
        return v.capitalize()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    uid: str


class UserPasswordReset(BaseResponse):
    task_id: str
