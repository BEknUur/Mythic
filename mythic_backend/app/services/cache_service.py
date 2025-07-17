import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

class CacheService:
    """Сервис для кэширования статусов и результатов обработки"""
    
    @staticmethod
    async def cache_processing_status(run_id: str, status_data: Dict[str, Any], ttl: int = 300):
        """Кэшировать статус обработки"""
        cache_key = f"processing_status:{run_id}"
        await redis_service.set(cache_key, status_data, ttl)
        logger.info(f"💾 Кэширован статус для {run_id}")
    
    @staticmethod
    async def get_processing_status(run_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус обработки из кэша"""
        cache_key = f"processing_status:{run_id}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def cache_user_books(user_id: str, books_data: Dict[str, Any], ttl: int = 1800):
        """Кэшировать книги пользователя"""
        cache_key = f"user_books:{user_id}"
        await redis_service.set(cache_key, books_data, ttl)
        logger.info(f"💾 Кэшированы книги для пользователя {user_id}")
    
    @staticmethod
    async def get_user_books(user_id: str) -> Optional[Dict[str, Any]]:
        """Получить книги пользователя из кэша"""
        cache_key = f"user_books:{user_id}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def invalidate_user_books(user_id: str):
        """Инвалидировать кэш книг пользователя"""
        cache_key = f"user_books:{user_id}"
        await redis_service.delete(cache_key)
        logger.info(f"🗑️ Инвалидирован кэш книг для пользователя {user_id}")
    
    @staticmethod
    async def cache_book_content(book_id: str, content: str, ttl: int = 7200):
        """Кэшировать содержимое книги"""
        cache_key = f"book_content:{book_id}"
        await redis_service.set(cache_key, content, ttl)
        logger.info(f"💾 Кэшировано содержимое книги {book_id}")
    
    @staticmethod
    async def get_book_content(book_id: str) -> Optional[str]:
        """Получить содержимое книги из кэша"""
        cache_key = f"book_content:{book_id}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def cache_instagram_data(profile_url: str, data: Dict[str, Any], ttl: int = 3600):
        """Кэшировать данные Instagram профиля"""
        cache_key = f"instagram_data:{hash(profile_url)}"
        await redis_service.set(cache_key, data, ttl)
        logger.info(f"💾 Кэшированы данные Instagram для {profile_url}")
    
    @staticmethod
    async def get_instagram_data(profile_url: str) -> Optional[Dict[str, Any]]:
        """Получить данные Instagram профиля из кэша"""
        cache_key = f"instagram_data:{hash(profile_url)}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def cache_ai_response(prompt: str, response: str, ttl: int = 1800):
        """Кэшировать ответы AI"""
        cache_key = f"ai_response:{hash(prompt)}"
        await redis_service.set(cache_key, response, ttl)
        logger.info(f"💾 Кэширован ответ AI для промпта")
    
    @staticmethod
    async def get_ai_response(prompt: str) -> Optional[str]:
        """Получить ответ AI из кэша"""
        cache_key = f"ai_response:{hash(prompt)}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def increment_request_counter(user_id: str, endpoint: str):
        """Инкрементировать счетчик запросов пользователя"""
        cache_key = f"request_count:{user_id}:{endpoint}"
        count = await redis_service.increment(cache_key)
        # Устанавливаем TTL на 1 час
        await redis_service.expire(cache_key, 3600)
        return count
    
    @staticmethod
    async def get_request_count(user_id: str, endpoint: str) -> int:
        """Получить количество запросов пользователя"""
        cache_key = f"request_count:{user_id}:{endpoint}"
        count = await redis_service.get(cache_key)
        return int(count) if count else 0
    
    @staticmethod
    async def cache_file_metadata(run_id: str, file_type: str, metadata: Dict[str, Any], ttl: int = 7200):
        """Кэшировать метаданные файлов"""
        cache_key = f"file_metadata:{run_id}:{file_type}"
        await redis_service.set(cache_key, metadata, ttl)
        logger.info(f"💾 Кэшированы метаданные файла {file_type} для {run_id}")
    
    @staticmethod
    async def get_file_metadata(run_id: str, file_type: str) -> Optional[Dict[str, Any]]:
        """Получить метаданные файла из кэша"""
        cache_key = f"file_metadata:{run_id}:{file_type}"
        return await redis_service.get(cache_key)
    
    @staticmethod
    async def clear_run_cache(run_id: str):
        """Очистить весь кэш для конкретного run_id"""
        # Получаем все ключи, связанные с run_id
        pattern = f"*:{run_id}:*"
        # В реальной реализации нужно использовать SCAN для поиска ключей
        # Пока просто удаляем основные ключи
        keys_to_delete = [
            f"processing_status:{run_id}",
            f"file_metadata:{run_id}:html",
            f"file_metadata:{run_id}:pdf",
            f"file_metadata:{run_id}:images"
        ]
        
        for key in keys_to_delete:
            await redis_service.delete(key)
        
        logger.info(f"🗑️ Очищен кэш для {run_id}")

# Глобальный экземпляр сервиса кэширования
cache_service = CacheService() 