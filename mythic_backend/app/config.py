from pydantic_settings import BaseSettings 
from typing import Optional

class Settings(BaseSettings):
    APIFY_TOKEN: str 
    ACTOR_ID: str 
    BACKEND_BASE: str
    
   
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str = "https://astana.openai.azure.com/"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    AZURE_OPENAI_GPT4_DEPLOYMENT: str = "gpt-4.1-mini"
    
    # Legacy OpenAI (if needed as backup)
    OPENAI_API_KEY: Optional[str] = None
    
    GOOGLE_API_KEY: str
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    
    # Database configuration
    DATABASE_URL:str
    ASYNC_DATABASE_URL: Optional[str]=None
    
    # Redis configuration
    REDIS_URL: str = "redis://redis:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 час по умолчанию
    REDIS_SESSION_TTL: int = 86400  # 24 часа для сессий

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
