from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Config:
    DB_URL = "postgresql+asyncpg://postgres:567234@localhost:5433/contacts_app"


config = Config()
