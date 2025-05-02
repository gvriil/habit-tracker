from telegram_bot.services.achievements import get_user_achievements, check_achievements
from telegram_bot.services.habits import (
    get_user_habits,
    save_habit,
    mark_habit_completed,
    mark_habit_skipped,
    delete_habit,
    update_habit,
    get_habits_for_notification,
    calculate_streak,
    get_habits_due_today,
    get_habit_details,
)
from telegram_bot.services.statistics import (
    get_user_statistics,
    get_weekly_report,
    get_habits_calendar,
)
