from typing import Dict, Any
import threading
import time


class UserDataStorage:
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._expiry_time = 3600  # 1 час

    def __getitem__(self, key):
        with self._lock:
            if key in self._data:
                return self._data[key]
            self._data[key] = {}
            return self._data[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = value

    def __contains__(self, key):
        with self._lock:
            return key in self._data

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def clear_expired(self):
        """Очищает устаревшие данные"""
        with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, value in self._data.items():
                if "last_activity" in value:
                    if current_time - value["last_activity"] > self._expiry_time:
                        expired_keys.append(key)

            for key in expired_keys:
                del self._data[key]

    def clear(self):
        with self._lock:
            self._data.clear()

    def update_activity(self, user_id):
        """Обновляет время последней активности пользователя"""
        with self._lock:
            if user_id in self._data:
                self._data[user_id]["last_activity"] = time.time()


# Создаем экземпляр для использования во всем приложении
# user_data = UserDataStorage()
# telegram_bot/user_data.py
user_data = {}  # Словарь для хранения данных пользователей


def get(chat_id, default=None):
    return user_data.get(chat_id, default)


def set(chat_id, data):
    user_data[chat_id] = data


def items():
    return user_data.items()


# Функции-обертки для совместимости
def get_user_data(user_id):
    return user_data[user_id]


def clear_user_data(user_id=None):
    if user_id is None:
        user_data.clear()
    else:
        user_data[user_id] = {}


def update_user_activity(user_id):
    user_data.update_activity(user_id)


def get_telegram_chat_id_by_user_id(user_id):
    """Получение chat_id пользователя Telegram по ID пользователя Django."""
    # Сначала пробуем найти в базе данных (основной источник)
    from users.models import User

    user = User.objects.filter(id=user_id).first()
    if user and user.telegram_id:
        return user.telegram_id

    # Как запасной вариант ищем в кеше сессий
    for chat_id, data in user_data.items():
        if data.get("user_id") == user_id:
            return chat_id

    return None
