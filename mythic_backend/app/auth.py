import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
import json
import base64

CLERK_SECRET_KEY = settings.CLERK_SECRET_KEY
CLERK_PUBLISHABLE_KEY = settings.CLERK_PUBLISHABLE_KEY

security = HTTPBearer()

class ClerkAuth:
    def __init__(self):
        self.jwks_url = f"https://api.clerk.dev/v1/jwks"
        self._jwks = None
        self.enabled = bool(CLERK_SECRET_KEY and CLERK_PUBLISHABLE_KEY)

    def get_jwks(self):
        if not self.enabled:
            return None
            
        if not self._jwks:
            try:
                response = requests.get(self.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()
            except Exception as e:
                print(f"Ошибка получения JWKS: {e}")
                self._jwks = None
        return self._jwks

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
      
        if not self.enabled:
            return {"sub": "anonymous", "clerk_disabled": True}
            
        try:
            if hasattr(jwt, 'decode'):
                payload = jwt.decode(token, options={"verify_signature": False})
            else:
                
                
                parts = token.split('.')
                if len(parts) != 3:
                    return None
                payload_part = parts[1]
                payload_part += '=' * (4 - len(payload_part) % 4)
                payload_bytes = base64.urlsafe_b64decode(payload_part)
                payload = json.loads(payload_bytes.decode('utf-8'))
            
            
            if "sub" not in payload: 
                return None
                
            return payload
        except Exception as e:
            print(f"Ошибка верификации токена: {e}")
            return None


clerk_auth = ClerkAuth()

def get_current_user(authorization: HTTPAuthorizationCredentials = security) -> Dict[str, Any]:
   
    if not clerk_auth.enabled:
        return {"sub": "anonymous", "clerk_disabled": True}
        
    if not authorization:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    token = authorization.credentials
    user_data = clerk_auth.verify_token(token)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    
    return user_data

def get_optional_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Опциональная зависимость для получения пользователя"""
    if not clerk_auth.enabled:
       
        return {"sub": "anonymous", "clerk_disabled": True}
        
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return clerk_auth.verify_token(token) 