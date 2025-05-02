import logging
import sys


def setup_logger():
    # Настройка логгера для бота
    logger = logging.getLogger("telegram_bot")
    logger.setLevel(logging.DEBUG)

    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Фор��ат сообщений
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


# Создаем логгер для импорта
bot_logger = setup_logger()
