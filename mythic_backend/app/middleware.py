import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware для кэширования и отслеживания запросов"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Получаем пользователя если есть
        user_id = None
        try:
            from app.auth import get_user_from_request
            user = get_user_from_request(request)
            if user:
                user_id = user.get("sub")
        except:
            pass
        
        # Отслеживаем запрос
        if user_id:
            endpoint = request.url.path
            await cache_service.increment_request_counter(user_id, endpoint)
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Логируем время выполнения
        execution_time = time.time() - start_time
        logger.info(f"⏱️ {request.method} {request.url.path} - {execution_time:.3f}s")
        
        # Добавляем заголовки для кэширования
        if request.url.path.startswith("/static/") or request.url.path.startswith("/view/"):
            response.headers["Cache-Control"] = "public, max-age=3600"  # 1 час для статических файлов
        elif request.url.path.startswith("/download/"):
            response.headers["Cache-Control"] = "public, max-age=86400"  # 24 часа для скачиваний
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения скорости запросов"""
    
    async def dispatch(self, request: Request, call_next):
        # Получаем пользователя если есть
        user_id = None
        try:
            from app.auth import get_user_from_request
            user = get_user_from_request(request)
            if user:
                user_id = user.get("sub")
        except:
            pass
        
        if user_id:
            endpoint = request.url.path
            request_count = await cache_service.get_request_count(user_id, endpoint)
            
            # Ограничения по эндпоинтам
            limits = {
                "/start-scrape": 10,  # 10 запросов в час
                "/status/": 100,      # 100 запросов в час
                "/books/my": 50,      # 50 запросов в час
            }
            
            for path, limit in limits.items():
                if endpoint.startswith(path) and request_count > limit:
                    logger.warning(f"🚫 Rate limit exceeded for user {user_id} on {endpoint}")
                    from fastapi import HTTPException
                    raise HTTPException(429, "Слишком много запросов. Попробуйте позже.")
        
        return await call_next(request) 