import os
from polar_sdk import Polar
from typing import Optional
import logging

log = logging.getLogger("polar")

class PolarService:
    def __init__(self):
        self.access_token = os.environ.get("POLAR_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("POLAR_ACCESS_TOKEN не найден в переменных окружения")
        
        self.polar = Polar(access_token=self.access_token)
        self.success_url = os.environ.get("POLAR_SUCCESS_URL", "http://localhost:5173/payment/success?checkout_id={CHECKOUT_ID}")
        self.cancel_url = os.environ.get("POLAR_CANCEL_URL", "http://localhost:5173/payment/cancel")
    
    def create_pro_subscription_checkout(self, customer_email: Optional[str] = None) -> str:
        """Создает checkout для Pro подписки"""
        try:
            product_id = os.environ.get("POLAR_PRO_MONTHLY_PRODUCT_ID")
            if not product_id:
                raise ValueError("POLAR_PRO_MONTHLY_PRODUCT_ID не найден")
            
            request_data = {
                "products": [product_id],
                "success_url": self.success_url,
                "cancel_url": self.cancel_url
            }
            
            if customer_email:
                request_data["customer_email"] = customer_email
            
            res = self.polar.checkouts.create(request=request_data)
            log.info(f"Создан Pro checkout: {res.id}")
            return res.url
            
        except Exception as e:
            log.error(f"Ошибка создания Pro checkout: {e}")
            raise
    
    def create_single_generation_checkout(self, customer_email: Optional[str] = None) -> str:
        """Создает checkout для разовой генерации"""
        try:
            product_id = os.environ.get("POLAR_SINGLE_GENERATION_PRODUCT_ID")
            if not product_id:
                raise ValueError("POLAR_SINGLE_GENERATION_PRODUCT_ID не найден")
            
            request_data = {
                "products": [product_id],
                "success_url": self.success_url,
                "cancel_url": self.cancel_url
            }
            
            if customer_email:
                request_data["customer_email"] = customer_email
            
            res = self.polar.checkouts.create(request=request_data)
            log.info(f"Создан single generation checkout: {res.id}")
            return res.url
            
        except Exception as e:
            log.error(f"Ошибка создания single generation checkout: {e}")
            raise
    
    def get_checkout_status(self, checkout_id: str) -> dict:
        """Получает статус checkout"""
        try:
            checkout = self.polar.checkouts.get(id=checkout_id)
            return {
                "id": checkout.id,
                "status": checkout.status,
                "customer_id": checkout.customer_id if hasattr(checkout, 'customer_id') else None,
                "customer_email": checkout.customer_email if hasattr(checkout, 'customer_email') else None,
                "products": checkout.products if hasattr(checkout, 'products') else []
            }
        except Exception as e:
            log.error(f"Ошибка получения статуса checkout {checkout_id}: {e}")
            raise

# Глобальный экземпляр сервиса
try:
    polar_service = PolarService()
except Exception as e:
    log.warning(f"Не удалось инициализировать PolarService: {e}")
    polar_service = None 