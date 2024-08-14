import os
from enum import Enum

from pydantic import AnyHttpUrl
from pydantic_settings import SettingsConfigDict, BaseSettings


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_USE_TLS: bool

    CRED_PATH: str
    FB_URL: AnyHttpUrl
    FB_BUCKET: str
    FB_API_KEY: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_EAGER: bool
    model_config = SettingsConfigDict(env_file=os.path.abspath("env/.prod.env"))


class DevelopmentConfig(Settings):
    ...


class ProductionConfig(Settings):
    ...


class TestingConfig(Settings):
    ...


settings = Settings()
