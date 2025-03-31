# token_management/api_client.py
import requests
from django.conf import settings
from .services import TokenService


class APIClient:
    def __init__(self):
        self.token_service = TokenService()

    def get_headers(self, user_id):
        """Получает заголовки с токеном авторизации"""
        token = self.token_service.get_user_token(user_id)
        if not token:
            return {}
        return {"Authorization": f"JWT {token}"}

    def make_request(self, user_id, method, endpoint, data=None):
        """Выполняет запрос к API с токеном авторизации"""
        headers = self.get_headers(user_id)
        url = f"{settings.API_BASE_URL}{endpoint}"

        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, json=data)
        elif method.lower() == "put":
            response = requests.put(url, headers=headers, json=data)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Неподдерживаемый метод запроса")

        return response