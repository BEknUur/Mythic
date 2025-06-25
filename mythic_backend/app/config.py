from pydantic_settings import BaseSettings 
from typing import Optional



class Settings(BaseSettings):
    APIFY_TOKEN:str 
    ACTOR_ID:str 
    BACKEND_BASE:str
    OPENAI_API_KEY:str 
    GOOGLE_API_KEY:str
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None

    class Config:
        env_file=".env"

settings=Settings()
