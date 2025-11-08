from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Get root directory (2 levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    HEALTHLAKE_DATASTORE_ID: str = "b1f04342d94dcc96c47f9528f039f5a8"
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True
        extra = 'ignore'  # Ignore extra fields from .env

settings = Settings()
