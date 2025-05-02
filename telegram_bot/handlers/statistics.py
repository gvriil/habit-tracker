from aiogram import Router, types
from aiogram.filters import Command

from telegram_bot.keyboards.keyboards import get_main_keyboard
from telegram_bot.services import get_user_statistics, get_user_achievements
from telegram_bot.utils.formatters import format_streak

router = Router()


@router.message(Command("stats"))
async def show_statistics(message: types.Message):
    """Показывает статистику привычек пользователя"""
    stats = await get_user_statistics(message.from_user.id)

    if not stats or stats.get("total_habits", 0) == 0:
        await message.answer(
            "<b>📊 У вас пока нет статистики</b>\n\n"
            "Создайте привычки и начните их отмечать, чтобы увидеть данные о вашем прогрессе.",
            reply_markup=get_main_keyboard(),
        )
        return

    stats_text = (
        "<b>📊 Ваша статистика</b>\n\n"
        f"<b>Всего привычек:</b> {stats['total_habits']}\n"
        f"<b>Выполнено сегодня:</b> {stats['completed_today']}/{stats['due_today']}\n"
        f"<b>Лучшая серия:</b> {format_streak(stats['max_streak'])}\n"
        f"<b>Всего выполнений:</b> {stats['total_completions']}\n\n"
    )

    # Добавляем информацию о лучшей привычке
    if stats.get("best_habit"):
        stats_text += f"<b>🏆 Лучшая привычка:</b> {stats['best_habit']['name']}\n"
        stats_text += (
            f"<b>Текущая серия:</b> {format_streak(stats['best_habit']['streak'])}\n\n"
        )

    # Добавляем информацию о привычке, требующей внимания
    if stats.get("worst_habit"):
        stats_text += f"<b>⚠️ Требует внимания:</b> {stats['worst_habit']['name']}\n"

    await message.answer(stats_text, reply_markup=get_main_keyboard())


@router.message(Command("achievements"))
async def show_achievements(message: types.Message):
    """Показывает достижения пользователя"""
    achievements = await get_user_achievements(message.from_user.id)

    if not achievements:
        # Если нет достижений, показываем заглушку
        achievements_text = (
            "<b>🏆 Ваши достижения</b>\n\n"
            "🔒 <b>Начало пути</b> - Создайте свою первую привычку\n"
            "🔒 <b>Недельная серия</b> - Выполняйте привычку 7 дней подряд\n"
            "🔒 <b>Месяц дисциплины</b> - Выполняйте привычку 30 дней подряд\n"
            "🔒 <b>Многозадачность</b> - Выполняйте 3 разные привычки в один день\n\n"
            "Продолжайте работать над своими привычками, чтобы разблокировать достижения!"
        )
    else:
        # Формируем список полученных достижений
        achievements_text = "<b>🏆 Ваши достижения</b>\n\n"

        for achievement in achievements:
            achievements_text += (
                f"{achievement['badge']} <b>{achievement['name']}</b> - "
                f"{achievement['description']}\n"
                f"📅 Получено: {achievement['date']}\n\n"
            )

    await message.answer(achievements_text, reply_markup=get_main_keyboard())
