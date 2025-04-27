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
                if 'last_activity' in value:
                    if current_time - value['last_activity'] > self._expiry_time:
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
                self._data[user_id]['last_activity'] = time.time()


# Создаем экземпляр для использования во всем приложении
user_data = UserDataStorage()


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