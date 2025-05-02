import logging

from django.apps import apps
from asgiref.sync import sync_to_async

# Настройка логгера
logger = logging.getLogger(__name__)

# Импорт моделей
User = apps.get_model("users", "User")
Habit = apps.get_model("habits", "Habit")
Achievement = apps.get_model("telegram_bot", "Achievement")
UserAchievement = apps.get_model("telegram_bot", "UserAchievement")


def check_achievements(user, habit, streak):
    """Проверяет и присваивает достижения пользователю."""
    achievement_data = None

    # Проверяем достижение для первой привычки
    habit_count = Habit.objects.filter(user=user).count()
    if habit_count == 1:
        achievement, created = Achievement.objects.get_or_create(
            code="first_habit",
            defaults={
                "name": "Начало пути",
                "description": "Создана первая привычка",
                "badge_emoji": "🌱",
            },
        )
        if (
            created
            or not UserAchievement.objects.filter(
                user=user, achievement=achievement
            ).exists()
        ):
            UserAchievement.objects.create(user=user, achievement=achievement)
            achievement_data = {
                "name": achievement.name,
                "description": achievement.description,
                "badge": achievement.badge_emoji,
            }

    # Достижение за серию в 7 дней
    if streak == 7:
        achievement, created = Achievement.objects.get_or_create(
            code="week_streak",
            defaults={
                "name": "Недельная серия",
                "description": "Выполняйте привычку 7 дней подряд",
                "badge_emoji": "🔥",
            },
        )
        if not UserAchievement.objects.filter(
            user=user, achievement=achievement, habit=habit
        ).exists():
            UserAchievement.objects.create(
                user=user, achievement=achievement, habit=habit
            )
            achievement_data = {
                "name": achievement.name,
                "description": achievement.description,
                "badge": achievement.badge_emoji,
            }

    # Достижение за серию в 30 дней
    elif streak == 30:
        achievement, created = Achievement.objects.get_or_create(
            code="month_streak",
            defaults={
                "name": "Месяц дисциплины",
                "description": "Выполняйте привычку 30 дней подряд",
                "badge_emoji": "🏆",
            },
        )
        if not UserAchievement.objects.filter(
            user=user, achievement=achievement, habit=habit
        ).exists():
            UserAchievement.objects.create(
                user=user, achievement=achievement, habit=habit
            )
            achievement_data = {
                "name": achievement.name,
                "description": achievement.description,
                "badge": achievement.badge_emoji,
            }

    return achievement_data


from asgiref.sync import sync_to_async


@sync_to_async
def get_user_achievements(telegram_id):
    """Получает достижения пользователя."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return []

        # Получаем достижения пользователя
        user_achievements = UserAchievement.objects.filter(user=user)

        result = []
        for ua in user_achievements:
            result.append(
                {
                    "name": ua.achievement.name,
                    "description": ua.achievement.description,
                    "badge": ua.achievement.badge_emoji,
                    "date": ua.created_at.strftime("%Y-%m-%d"),
                }
            )

        return result

    except Exception as e:
        logger.error(f"Ошибка при получении достижений: {e}")
        return []
