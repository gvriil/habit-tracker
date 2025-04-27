from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from telegram_bot.keyboards.keyboards import get_main_keyboard

router = Router()

from aiogram import F
from aiogram.fsm.context import FSMContext


@router.message(F.text == "⬅️ Назад")
async def back_button(message: types.Message, state: FSMContext):
    # Сбрасываем состояние и возвращаемся в главное меню
    await state.clear()
    await message.answer("Действие отменено", reply_markup=get_main_keyboard())
    await cmd_start(message)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start с созданием пользователя"""
    # Создаем пользователя, если его не существует
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"

    # Создаем пользователя асинхронно
    await create_user_if_not_exists(user_id, username)

    await message.answer(
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        f"Я бот для отслеживания привычек и достижения целей.\n\n"
        f"<b>Что я умею:</b>\n"
        f"• Помогать создавать полезные привычки\n"
        f"• Отправлять напоминания в нужное время\n"
        f"• Отслеживать серии выполнений\n"
        f"• Показывать статистику и достижения\n\n"
        f"Используйте кнопки меню или команду /help для справки.",
        reply_markup=get_main_keyboard()
    )


async def create_user_if_not_exists(user_id, username):
    """Создаёт пользователя в Django, если его не существует"""

    @sync_to_async
    def _create_user():
        from django.contrib.auth import get_user_model
        import logging
        logger = logging.getLogger('django')

        User = get_user_model()
        if not User.objects.filter(id=user_id).exists():
            try:
                # Создаем пользователя с id из Telegram
                user = User.objects.create(
                    id=user_id,
                    username=username[:150],  # Обрезаем, если слишком длинное
                    is_active=True
                )
                logger.error(f"Создан новый пользователь: {user.id}")
                return True
            except Exception as e:
                logger.error(f"Ошибка создания пользователя: {e}")
                return False
        return True

    return await _create_user()


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "<b>📚 Справка по командам</b>\n\n"
        "/start - Начало работы с ботом\n"
        "/help - Эта справка\n"
        "/habits - Список ваших привычек\n"
        "/new_habit - Создать новую привычку\n"
        "/stats - Ваша статистика\n"
        "/achievements - Ваши достижения\n\n"
        "<b>🤔 Как пользоваться ботом:</b>\n"
        "1. Создайте привычку кнопкой <b>➕ Новая привычка</b>\n"
        "2. Бот будет присылать напоминания в указанное время\n"
        "3. Отмечайте выполнение с помощью кнопки ✅\n"
        "4. Следите за своими сериями и получайте достижения\n\n"
        "<b>💡 Совет:</b> Начните с малого - одна простая привычка на 5 минут в день!"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())


@router.message(F.text == "❓ Помощь")
async def help_button(message: types.Message):
    """Обработка нажатия кнопки помощи"""
    await cmd_help(message)


@router.message(F.text == "📋 Мои привычки")
async def habits_button(message: types.Message):
    """Обработка нажатия кнопки списка привычек"""
    from telegram_bot.handlers.habits import show_habits_list
    await show_habits_list(message)


@router.message(F.text == "➕ Новая привычка")
async def new_habit_button(message: types.Message, state: FSMContext):
    """Обработка нажатия кнопки создания привычки"""
    from telegram_bot.handlers.habits import create_new_habit
    await create_new_habit(message, state)


@router.message(F.text == "📊 Статистика")
async def stats_button(message: types.Message):
    """Обработка нажатия кнопки статистики"""
    from telegram_bot.handlers.statistics import show_statistics
    await show_statistics(message)


@router.message(F.text == "🏆 Достижения")
async def achievements_button(message: types.Message):
    """Обработка нажатия кнопки достижений"""
    from telegram_bot.handlers.statistics import show_achievements
    await show_achievements(message)
