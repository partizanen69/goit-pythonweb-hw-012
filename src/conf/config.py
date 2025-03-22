from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # database
    DB_URL: str = os.getenv("DATABASE_URL", "")
    # jwt
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # email
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: SecretStr = SecretStr(os.getenv("MAIL_PASSWORD", ""))
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "465"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.meta.ua")


settings = Settings()
