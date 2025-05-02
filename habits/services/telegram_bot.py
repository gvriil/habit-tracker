# habits/services/telegram_bot.py
import logging

import telegram
from django.conf import settings

# Настройка логгера
logger = logging.getLogger(__name__)

# Инициализация бота (для совместимости с тестами)
bot = None
if hasattr(settings, "TELEGRAM_BOT_TOKEN") and settings.TELEGRAM_BOT_TOKEN:
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_habit_reminder(habit):
    """Отправляет напоминание о привычке через Telegram."""
    chat_id = habit.user.telegram_chat_id
    if not chat_id:
        logger.warning(f"Не найден telegram_chat_id для пользователя {habit.user.id}")
        return False

    message = f"Напоминание: {habit.name} в {habit.place}"
    logger.info(f"Отправка сообщения в чат {chat_id}: {message}")

    try:
        # Проверяем инициализацию бота
        if not bot:
            logger.error("Telegram bot не инициализирован")
            return False

        bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return False
