from aiogram import Dispatcher, types
from aiogram.utils.chat_action import ChatActionMiddleware

from telegram_bot.handlers.base import router as base_router
from telegram_bot.handlers.habits import router as habits_router
from telegram_bot.handlers.statistics import router as statistics_router
from telegram_bot.handlers.notifications import router as notifications_router

# Создаём отдельный роутер для необработанных сообщений
from aiogram import Router

fallback_router = Router(name="fallback_router")


@fallback_router.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "Я не понимаю эту команду. Используйте /help для списка доступных команд."
    )


def register_all_handlers(dp):
    """Регистрация всех обработчиков"""
    # Добавляем middleware для отображения "печатает..."
    # from telegram_bot.handlers.habits import router as habits_router
    # dp.include_router(habits_router)
    dp.message.middleware(ChatActionMiddleware())

    # Удаляем неработающую строку приоритизации
    # base_router.message.filter.update_handler_flags({"commands": ["start", "help"]})

    # Регистрируем роутеры в правильном порядке
    # важно, что base_router первый - его обработчики имеют приоритет
    dp.include_router(base_router)
    dp.include_router(habits_router)
    dp.include_router(statistics_router)
    dp.include_router(notifications_router)

    # Fallback роутер должен быть последним
    dp.include_router(fallback_router)
