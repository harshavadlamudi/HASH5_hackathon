from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    HEALTHLAKE_DATASTORE_ID: str = "b1f04342d94dcc96c47f9528f039f5a8"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
