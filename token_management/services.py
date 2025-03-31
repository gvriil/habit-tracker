# token_management/services.py
import jwt
import redis
from django.conf import settings
from datetime import datetime, timedelta


class TokenService:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.CELERY_BROKER_URL)

    def store_user_token(self, user_id, token, token_type="access"):
        """Сохраняет токен в Redis"""
        # Декодирование токена для получения срока действия
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded.get("exp", 0)

        # Рассчитываем время жизни токена в секундах
        current_timestamp = datetime.now().timestamp()
        ttl = max(1, int(exp_timestamp - current_timestamp))

        # Сохраняем токен с установленным временем жизни
        key = f"{token_type}_token:{user_id}"
        self.redis.setex(key, ttl, token)
        return True

    def get_user_token(self, user_id, token_type="access"):
        """Получает токен пользователя из Redis"""
        key = f"{token_type}_token:{user_id}"
        token = self.redis.get(key)
        if token:
            return token.decode('utf-8')
        return None

    def delete_user_tokens(self, user_id):
        """Удаляет все токены пользователя"""
        self.redis.delete(f"access_token:{user_id}")
        self.redis.delete(f"refresh_token:{user_id}")
        return True