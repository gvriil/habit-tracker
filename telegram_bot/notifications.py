# telegram_bot/notifications.py

import os
import logging
from telegram import Bot, ParseMode
from dotenv import load_dotenv
from . import user_data

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка токена бота
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def send_notification(user_id, message_text, parse_mode=ParseMode.MARKDOWN):
    """Отправка уведомления пользователю."""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        telegram_chat_id = get_chat_id_by_user(user_id)

        if telegram_chat_id:
            try:
                bot.send_message(
                    chat_id=telegram_chat_id, text=message_text, parse_mode=parse_mode
                )
                logger.info(f"Отправлено уведомление пользователю {user_id}")
                return True
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")
                return False
        else:
            logger.warning(f"Не найден telegram_chat_id для пользователя {user_id}")
            return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке уведомления: {e}")
        return False


def get_chat_id_by_user(user_id):
    """Получение chat_id пользователя Telegram по ID пользователя Django."""
    telegram_chat_id = None
    for chat_id, data in user_data.items():
        if data.get("user_id") == user_id:
            telegram_chat_id = chat_id
            break
    return telegram_chat_id
