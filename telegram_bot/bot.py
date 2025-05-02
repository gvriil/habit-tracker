import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from telegram_bot.config import set_commands
from telegram_bot.handlers import register_all_handlers

# Настройка Django перед импортом моделей
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    # Получаем токен из переменных окружения
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        logger.error("Не задан TELEGRAM_TOKEN")
        return

    # Инициализация хранилища состояний
    storage = MemoryStorage()

    # Инициализируем диспетчер и бота
    dp = Dispatcher(storage=storage)
    bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode="HTML"))

    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(
            f"Инициализация бота успешна. Имя: {bot_info.full_name} (@{bot_info.username})"
        )

        # Устанавливаем команды бота
        await set_commands(bot)

        # Регистрируем обработчики
        register_all_handlers(dp)

        # Запускаем бота в режиме поллинга
        logger.info("Запуск бота в режиме long polling")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()
