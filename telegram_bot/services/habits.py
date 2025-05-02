import logging
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from django.apps import apps

# Настройка логгера
logger = logging.getLogger(__name__)

# Импорт моделей
User = apps.get_model("users", "User")
Habit = apps.get_model("habits", "Habit")
HabitCompletion = apps.get_model("habits", "HabitCompletion")


# Импорт функций для проверки достижений


@sync_to_async
def get_user_habits(telegram_id):
    """Получение привычек пользователя с статистикой"""
    try:
        # Получаем пользователя по telegram_id
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            logger.warning(f"Пользователь с Telegram ID {telegram_id} не найден")
            return []

        # Получаем привычки с базовой информацией
        habits = Habit.objects.filter(user=user).order_by("-created_at")

        # Форматируем данные для ответа
        result = []
        for habit in habits:
            # Расчет серии (streak)
            streak = calculate_streak(habit)

            result.append(
                {
                    "id": habit.id,
                    "name": habit.name,
                    "category": habit.category,
                    "time_of_day": habit.time_of_day,
                    "frequency": habit.frequency,
                    "created_at": habit.created_at.strftime("%Y-%m-%d"),
                    "streak": streak,
                }
            )

        return result
    except Exception as e:
        logger.error(f"Ошибка при получении привычек: {e}")
        return []


@sync_to_async
def save_habit(user_id, name, category, time_of_day, frequency):
    """Сохранение новой привычки."""
    try:
        # Получаем или создаем пользователя
        try:
            user = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Пользователь с Telegram ID {user_id} не найден")
            return None

        # Создаем привычку
        habit = Habit.objects.create(
            user=user,
            name=name,
            category=category,
            time_of_day=time_of_day,
            frequency=frequency,
        )
        return habit
    except Exception as e:
        logger.error(f"Ошибка при сохранении привычки: {e}")
        return None


@sync_to_async
def mark_habit_completed(telegram_id, habit_id):
    """Отметить привычку как выполненную."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return {"success": False, "error": "Пользователь не найден"}

        # Получаем привычку и проверяем принадлежность пользователю
        try:
            habit = Habit.objects.get(id=habit_id, user=user)
        except Habit.DoesNotExist:
            return {"success": False, "error": "Привычка не найдена"}

        # Создаем запись о выполнении
        today = datetime.now().date()
        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit, date=today, defaults={"status": "completed"}
        )

        if not created:
            completion.status = "completed"
            completion.save()

        # Рассчитываем текущую серию
        streak = calculate_streak(habit)

        # Проверяем достижения (импортируем из achievements.py)
        from telegram_bot.services.achievements import check_achievements

        achievement = check_achievements(user, habit, streak)

        return {"success": True, "streak": streak, "achievement": achievement}

    except Exception as e:
        logger.error(f"Ошибка при отметке привычки: {e}")
        return {"success": False, "error": str(e)}


@sync_to_async
def mark_habit_skipped(telegram_id, habit_id):
    """Отметить привычку как пропущенную."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return {"success": False, "error": "Пользователь не найден"}

        # Получаем привычку и проверяем принадлежность пользователю
        try:
            habit = Habit.objects.get(id=habit_id, user=user)
        except Habit.DoesNotExist:
            return {"success": False, "error": "Привычка не найдена"}

        # Создаем запись о пропуске
        today = datetime.now().date()
        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit, date=today, defaults={"status": "skipped"}
        )

        if not created:
            completion.status = "skipped"
            completion.save()

        return {"success": True}

    except Exception as e:
        logger.error(f"Ошибка при пропуске привычки: {e}")
        return {"success": False, "error": str(e)}


@sync_to_async
def delete_habit(telegram_id, habit_id):
    """Удаляет привычку пользователя."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return False, "Пользователь не найден"

        # Получаем привычку и проверяем принадлежность пользователю
        try:
            habit = Habit.objects.get(id=habit_id, user=user)
        except Habit.DoesNotExist:
            return False, "Привычка не найдена"

        # Удаляем привычку
        habit.delete()
        return True, "Привычка успешно удалена"

    except Exception as e:
        logger.error(f"Ошибка при удалении привычки: {e}")
        return False, str(e)


@sync_to_async
def update_habit(telegram_id, habit_id, **kwargs):
    """Обновляет данные привычки."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return False, "Пользователь не найден"

        # Получаем привычку и проверяем принадлежность пользователю
        try:
            habit = Habit.objects.get(id=habit_id, user=user)
        except Habit.DoesNotExist:
            return False, "Привычка не найдена"

        # Обновляем поля привычки
        for key, value in kwargs.items():
            if hasattr(habit, key):
                setattr(habit, key, value)

        habit.save()
        return True, "Привычка успешно обновлена"

    except Exception as e:
        logger.error(f"Ошибка при обновлении привычки: {e}")
        return False, str(e)


@sync_to_async
def get_habits_for_notification(current_time):
    """Получает список привычек для отправки уведомлений."""
    try:
        # Получаем текущий час
        hour = current_time.hour
        # Получаем день недели (0-6, где 0 - понедельник)
        weekday = current_time.weekday()

        # Определяем время дня для текущего часа
        time_of_day = "morning"
        if 12 <= hour < 17:
            time_of_day = "day"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        elif hour >= 22 or hour < 5:
            time_of_day = "night"

        # Получаем привычки для текущего времени дня
        habits = Habit.objects.filter(time_of_day=time_of_day)

        # Фильтруем по частоте
        result = []
        for habit in habits:
            is_due = False

            if habit.frequency == "daily":
                is_due = True
            elif habit.frequency == "weekdays" and weekday < 5:  # Пн-Пт
                is_due = True
            elif habit.frequency == "weekends" and weekday >= 5:  # Сб-Вс
                is_due = True
            elif habit.frequency == "custom" and habit.custom_days:
                custom_days = [int(d) for d in habit.custom_days.split(",")]
                is_due = weekday in custom_days

            if is_due:
                # Проверяем, не отмечена ли привычка уже сегодня
                if not HabitCompletion.objects.filter(
                    habit=habit, date=current_time.date()
                ).exists():
                    result.append(
                        {
                            "user_id": habit.user.telegram_id,
                            "habit_id": habit.id,
                            "name": habit.name,
                        }
                    )

        return result

    except Exception as e:
        logger.error(f"Ошибка при получении привычек для уведомлений: {e}")
        return []


def calculate_streak(habit):
    """Функция для расчета текущей серии выполнений привычки."""
    today = datetime.now().date()
    completions = HabitCompletion.objects.filter(
        habit=habit, status="completed"
    ).order_by("-date")[
        :30
    ]  # Берем последние 30 выполнений

    streak = 0
    last_date = today + timedelta(days=1)  # Начинаем с "завтра"

    for comp in completions:
        # Если дата следующая за последней или это первая итерация и сегодняшнее выполнение
        if ((last_date - comp.date).days == 1) or (
            last_date > today and comp.date == today
        ):
            streak += 1
            last_date = comp.date
        else:
            break

    return streak


def get_habits_due_today(habits, date):
    """Определяет, какие привычки должны быть выполнены в указанную дату."""
    weekday = date.weekday()  # 0-6, где 0 - понедельник
    due_habits = []

    for habit in habits:
        is_due = False

        # Проверяем частоту привычки
        if habit.frequency == "daily":
            is_due = True
        elif habit.frequency == "weekdays" and weekday < 5:  # Пн-Пт
            is_due = True
        elif habit.frequency == "weekends" and weekday >= 5:  # Сб-Вс
            is_due = True
        elif habit.frequency == "custom" and habit.custom_days:
            # Предполагается, что custom_days хранит дни недели как строку "0,2,4"
            custom_days = [int(d) for d in habit.custom_days.split(",")]
            is_due = weekday in custom_days

        if is_due:
            due_habits.append(habit)

    return due_habits


def get_habit_details(habit_id):
    """
    Получает подробную информацию о привычке по id
    """
    from habits.models import Habit

    try:
        return Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        return None


@sync_to_async
def create_habit(user_id, name, category, frequency, time_value):
    """Создание тестовой привычки"""
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        from habits.models import Habit

        user = User.objects.get(id=user_id)

        # Создаем привычку, используя правильные поля модели
        habit = Habit.objects.create(
            user=user,
            name=name,
            category=category,
            frequency=frequency,
            time_of_day=time_value,  # Используем time_of_day вместо time
        )

        return habit
    except Exception as e:
        logger.error(f"Ошибка при создании привычки: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return None
