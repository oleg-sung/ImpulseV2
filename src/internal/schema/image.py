import base64

from pydantic import BaseModel, field_validator, model_validator


class Image(BaseModel):
    file: str
    content_type: str
    size: int

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        allowed_extensions = ["image/png", "image/jpg", "image/jpeg"]
        if v not in allowed_extensions:
            raise ValueError("Invalid content type")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if v >= 1000000:
            raise ValueError("size must be less than 1 mb")
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_file(cls, v):
        v["file"] = base64.b64encode(v["file"]).decode("utf-8")
        return v
