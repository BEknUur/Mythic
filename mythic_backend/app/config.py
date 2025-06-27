from pydantic_settings import BaseSettings 
from typing import Optional





class Settings(BaseSettings):
    APIFY_TOKEN: str 
    ACTOR_ID: str 
    BACKEND_BASE: str
    OPENAI_API_KEY: str 
    GOOGLE_API_KEY: str
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    
    # Database configuration
    DATABASE_URL:str
    ASYNC_DATABASE_URL: Optional[str]=None

    class Config:
        env_file = ".env"
    
    @property
    def get_async_database_url(self) -> str:
        """Get async database URL, deriving from DATABASE_URL if ASYNC_DATABASE_URL is not set"""
        if self.ASYNC_DATABASE_URL:
            return self.ASYNC_DATABASE_URL
        
        # Convert sync URL to async URL
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return "postgresql+asyncpg://mythic_user:mythic_password@localhost:5432/mythic_db"

settings = Settings()
