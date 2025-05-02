# Импортируем основные настройки

# Переопределяем базу данных на SQLite в памяти для быстрых тестов
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # Использование базы в памяти
    }
}
