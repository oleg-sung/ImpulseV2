import datetime
import re
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
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{6,8}$"
        if not bool(re.match(password_regex, self.password)):
            raise ValueError("Password must be between 6 and 8 characters")
        return self

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str):
        pattern = r"^[а-яА-ЯёЁ\-]+$"
        if not re.match(pattern, v):
            raise ValueError('Value has to consist of Cyrillic letters')
        return v.capitalize()

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, v):
        if v is None:
            return v

        today = datetime.date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 5:
            raise ValueError("Age must be at least 5 years old")
        elif age > 80:
            raise ValueError("Age must be no more than 5 years old")

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    uid: str


class UserPasswordReset(BaseResponse):
    task_id: str


class ChangePassword(BaseModel):
    password: str
    new_password: str

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def password_complexity(self):
        result = len(self.new_password)
        if 6 > result or result > 8:
            raise ValueError("Password must be between 6 and 8 characters")
        return self
