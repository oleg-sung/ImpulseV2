import re
import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator

from pkg.firebase_tools.tools import FirestoreTools


class UserType(str, Enum):
    """
    Enumeration of possible user
    """

    PLAYER = "player"
    COACH = "coach"
    ADMIN = "admin"


class UserCreate(BaseModel):
    user_type: UserType = Field(default=UserType.ADMIN, alias="userType")
    email: EmailStr
    password: str
    first_name: str = Field(max_items=12, min_length=2, alias="firstName")
    middle_name: Optional[str] = Field(
        default=None, max_length=12, min_length=2, alias="middleName"
    )
    last_name: str = Field(max_length=20, min_length=2, alias="lastName")
    birthdate: datetime.date
    phone: str
    info: Optional[str] = None
    club_name: str

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def validate_phone_number(self):
        if not self.phone.isdigit():
            raise ValueError("Номер телефона должен содержать только цифры")
        return self

    @model_validator(mode="after")
    def password_complexity(self):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!#%?&]+$"
        if not re.match(pattern, self.password):
            raise ValueError(
                "Password must contain at least one lowercase letter,"
                " one uppercase letter, one digit, and one special character."
            )
        return self

    @model_validator(mode="after")
    def validate_club_name(self):
        result = (
            FirestoreTools()
            .get_collection("club")
            .where("name", "==", self.club_name)
            .get()
        )
        if result:
            raise ValueError("Club name already")
        return self

    @field_validator("first_name", "last_name", "middle_name")
    @classmethod
    def validate_name(cls, v: str):
        return v.capitalize()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    uid: str


class UserPasswordReset(BaseModel):
    task_id: str
    status: bool


class UserCreateTast(BaseModel):
    task_id: str
