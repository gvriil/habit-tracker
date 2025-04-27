def format_streak(days: int) -> str:
    """Форматирование количества дней в русском склонении"""
    if 11 <= days % 100 <= 19:
        return f"{days} дней"
    elif days % 10 == 1:
        return f"{days} день"
    elif 2 <= days % 10 <= 4:
        return f"{days} дня"
    else:
        return f"{days} дней"


def get_emoji_for_category(category: str) -> str:
    """Возвращает эмодзи для категории привычки"""
    emoji_map = {
        "health": "🥗",
        "sport": "💪",
        "study": "📚",
        "self": "🧠",
        "other": "🔄"
    }
    return emoji_map.get(category, "⚪")


def get_emoji_for_frequency(frequency: str) -> str:
    """Возвращает эмодзи для частоты привычки"""
    emoji_map = {
        "daily": "🔄",
        "weekdays": "📅",
        "weekends": "🏖️",
        "custom": "📆"
    }
    return emoji_map.get(frequency, "⚪")


def format_habit_notification(habit_name: str) -> str:
    """Форматирует уведомление о привычке с мотивационной фразой"""
    import random

    motivational_phrases = [
        "Пришло время для действий! 💪",
        "Маленькие шаги - большие результаты! 🌱",
        "Сделайте это сейчас - и день станет лучше! ✨",
        "Помните о своих целях! 🎯",
        "Ваша дисциплина формирует будущее! 🚀",
        "Каждое действие приближает к цели! 🏆",
    ]

    return f"🔔 <b>Напоминание!</b>\n\n<b>{habit_name}</b>\n\n{random.choice(motivational_phrases)}"