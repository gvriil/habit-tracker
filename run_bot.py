import os
import django
import asyncio

# Настройка окружения для локального запуска
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DB_HOST", "localhost")  # Переопределяем хост БД
django.setup()

if __name__ == "__main__":
    from telegram_bot.bot import main

    asyncio.run(main())
