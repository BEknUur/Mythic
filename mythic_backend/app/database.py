from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
from .config import settings
from typing import AsyncGenerator

# URL базы данных из настроек
DATABASE_URL = settings.DATABASE_URL
ASYNC_DATABASE_URL = settings.get_async_database_url

# Синхронный движок (для миграций и инициализации)
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,  # Установите True для логирования SQL запросов
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Асинхронный движок (для основной работы)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Установите True для логирования SQL запросов
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def create_tables():
    """Создать все таблицы в базе данных"""
    Base.metadata.create_all(bind=sync_engine)

def get_sync_db() -> Session:
    """Получить синхронную сессию базы данных"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Получить асинхронную сессию базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Зависимость для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI для получения сессии базы данных"""
    async for session in get_async_db():
        yield session 