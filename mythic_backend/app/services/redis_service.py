import json
import pickle
from typing import Any, Optional, Union
import aioredis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._connection_pool = None
    
    async def connect(self):
        """Подключение к Redis"""
        if not self.redis:
            try:
                self.redis = aioredis.from_url(
                    "redis://redis:6379",
                    encoding="utf-8",
                    decode_responses=True
                )
                # Проверяем подключение
                await self.redis.ping()
                logger.info("✅ Redis подключен успешно")
            except Exception as e:
                logger.error(f"❌ Ошибка подключения к Redis: {e}")
                self.redis = None
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Установить значение в кэш"""
        if not self.redis:
            await self.connect()
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Ошибка установки значения в Redis: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if not self.redis:
            await self.connect()
        
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
        except Exception as e:
            logger.error(f"Ошибка получения значения из Redis: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Удалить ключ из кэша"""
        if not self.redis:
            await self.connect()
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления ключа из Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Ошибка проверки существования ключа в Redis: {e}")
            return False
    
    async def set_hash(self, key: str, mapping: dict, expire: int = 3600) -> bool:
        """Установить хэш в кэш"""
        if not self.redis:
            await self.connect()
        
        try:
            # Сериализуем значения в JSON
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v, ensure_ascii=False)
                else:
                    serialized_mapping[k] = str(v)
            
            await self.redis.hset(key, mapping=serialized_mapping)
            await self.redis.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"Ошибка установки хэша в Redis: {e}")
            return False
    
    async def get_hash(self, key: str) -> Optional[dict]:
        """Получить хэш из кэша"""
        if not self.redis:
            await self.connect()
        
        try:
            hash_data = await self.redis.hgetall(key)
            if not hash_data:
                return None
            
            # Десериализуем значения из JSON
            result = {}
            for k, v in hash_data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            
            return result
        except Exception as e:
            logger.error(f"Ошибка получения хэша из Redis: {e}")
            return None
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Инкрементировать счетчик"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            logger.error(f"Ошибка инкремента в Redis: {e}")
            return None
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Установить время жизни ключа"""
        if not self.redis:
            await self.connect()
        
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Ошибка установки времени жизни в Redis: {e}")
            return False

# Глобальный экземпляр Redis сервиса
redis_service = RedisService()

# Декоратор для кэширования
def cache_result(prefix: str, expire: int = 3600):
    """Декоратор для кэширования результатов функций"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Создаем ключ кэша на основе аргументов
            cache_key = f"{prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Пытаемся получить из кэша
            cached_result = await redis_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"📦 Кэш HIT для {cache_key}")
                return cached_result
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            await redis_service.set(cache_key, result, expire)
            logger.info(f"💾 Кэш SAVE для {cache_key}")
            
            return result
        return wrapper
    return decorator 