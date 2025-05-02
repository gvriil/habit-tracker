from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="habits", description="Мои привычки"),
        BotCommand(command="new_habit", description="Создать привычку"),
        BotCommand(command="stats", description="Моя статистика"),
    ]
    await bot.set_my_commands(commands)
