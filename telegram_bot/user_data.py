"""
Модуль для хранения данных пользователей Telegram бота
"""

# Хранилище данных пользователей
user_data = {}

# Экспортируем словарные операции на уровень модуля
def __iter__():
    return iter(user_data)

def __getitem__(key):
    return user_data[key]

def __setitem__(key, value):
    user_data[key] = value

def __delitem__(key):
    del user_data[key]

def __contains__(item):
    return item in user_data

def items():
    return user_data.items()

def keys():
    return user_data.keys()

def values():
    return user_data.values()

def get(key, default=None):
    return user_data.get(key, default)

def clear():
    user_data.clear()

def update(*args, **kwargs):
    user_data.update(*args, **kwargs)

def copy():
    return user_data.copy()

# Вспомогательные функции
def get_user_data(user_id):
    """Получение данных пользователя. Если данных нет, создается пустой словарь."""
    if user_id not in user_data:
        user_data[user_id] = {}
    return user_data[user_id]

def set_user_data(user_id, key, value):
    """Установка данных пользователя."""
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value
    return True

def clear_user_data(user_id):
    """Очистка данных пользователя."""
    if user_id in user_data:
        user_data.pop(user_id)
    return True