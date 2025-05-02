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


# В файл telegram_bot/services/statistics.py добавить:


@sync_to_async
def get_user_statistics(telegram_id):
    """Получение статистики пользователя."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None

        # Текущая дата
        today = datetime.now().date()

        # Получаем все привычки пользователя
        habits = Habit.objects.filter(user=user)

        if not habits.exists():
            return {"total_habits": 0}

        # Общее количество привычек
        total_habits = habits.count()

        # Получаем привычки, которые должны быть выполнены сегодня
        from telegram_bot.services.habits import get_habits_due_today

        due_today_count = len(get_habits_due_today(habits, today))

        # Получаем привычки, которые выполнены сегодня
        completed_today = HabitCompletion.objects.filter(
            habit__in=habits, date=today, status="completed"
        ).count()

        # Получаем лучшую привычку (с наибольшей серией)
        best_habit = None
        best_streak = 0
        worst_habit = None
        worst_days = 999

        # Импортируем функцию для расчета серии
        from telegram_bot.services.habits import calculate_streak

        for habit in habits:
            # Рассчитываем текущую серию
            streak = calculate_streak(habit)

            if streak > best_streak:
                best_streak = streak
                best_habit = habit

            # Дней с последнего выполнения
            last_completion = (
                HabitCompletion.objects.filter(habit=habit, status="completed")
                .order_by("-date")
                .first()
            )

            days_since_last = 999
            if last_completion:
                days_since_last = (today - last_completion.date).days

            if 0 < days_since_last < worst_days:
                worst_days = days_since_last
                worst_habit = habit

        # Общее количество выполнений
        total_completions = HabitCompletion.objects.filter(
            habit__in=habits, status="completed"
        ).count()

        # Формируем результат
        result = {
            "total_habits": total_habits,
            "due_today": due_today_count,
            "completed_today": completed_today,
            "max_streak": best_streak,
            "total_completions": total_completions,
        }

        if best_habit:
            result["best_habit"] = {
                "id": best_habit.id,
                "name": best_habit.name,
                "streak": best_streak,
            }

        if worst_habit:
            result["worst_habit"] = {
                "id": worst_habit.id,
                "name": worst_habit.name,
                "days_since": worst_days,
            }

        return result
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return None


@sync_to_async
def get_weekly_report(telegram_id):
    """Генерирует еженедельный отчет для пользователя."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None

        # Текущая дата и неделю назад
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # Получаем все привычки пользователя
        habits = Habit.objects.filter(user=user)

        if not habits.exists():
            return {
                "has_data": False,
                "message": "У вас еще нет привычек для формирования отчета",
            }

        # Статистика выполнений за текущую неделю
        completions_this_week = HabitCompletion.objects.filter(
            habit__in=habits, status="completed", date__gte=week_ago, date__lte=today
        ).count()

        # Сравнение с предыдущей неделей
        prev_week_start = week_ago - timedelta(days=7)
        completions_prev_week = HabitCompletion.objects.filter(
            habit__in=habits,
            status="completed",
            date__gte=prev_week_start,
            date__lt=week_ago,
        ).count()

        # Расчет разницы в процентах
        if completions_prev_week > 0:
            change_percent = (
                (completions_this_week - completions_prev_week) / completions_prev_week
            ) * 100
        else:
            change_percent = 100 if completions_this_week > 0 else 0

        # Лучшая привычка недели
        best_habit = None
        best_completions = 0

        for habit in habits:
            habit_completions = HabitCompletion.objects.filter(
                habit=habit, status="completed", date__gte=week_ago, date__lte=today
            ).count()

            if habit_completions > best_completions:
                best_completions = habit_completions
                best_habit = habit

        result = {
            "has_data": True,
            "period": {
                "start": week_ago.strftime("%d.%m.%Y"),
                "end": today.strftime("%d.%m.%Y"),
            },
            "total_completions": completions_this_week,
            "change_percent": round(change_percent, 1),
            "change_direction": "up" if change_percent >= 0 else "down",
        }

        if best_habit:
            result["best_habit"] = {
                "id": best_habit.id,
                "name": best_habit.name,
                "completions": best_completions,
            }

        return result

    except Exception as e:
        logger.error(f"Ошибка при генерации еженедельного отчета: {e}")
        return None


@sync_to_async
def get_habits_calendar(telegram_id, habit_id=None, month=None, year=None):
    """Получает данные для календаря привычек."""
    try:
        # Получаем пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None

        # Если не указан месяц или год, используем текущие
        if not month or not year:
            now = datetime.now()
            month = month or now.month
            year = year or now.year

        # Формируем даты начала и конца месяца
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

        # Формируем фильтр для привычек
        habits_filter = {"user": user}
        if habit_id:
            habits_filter["id"] = habit_id

        # Получаем привычки
        habits = Habit.objects.filter(**habits_filter)

        if not habits.exists():
            return None

        # Получаем выполнения за указанный месяц
        completions = HabitCompletion.objects.filter(
            habit__in=habits, date__gte=start_date, date__lte=end_date
        )

        # Группируем данные по датам
        calendar_data = {}
        for day in range(1, end_date.day + 1):
            date = datetime(year, month, day).date()
            calendar_data[day] = {
                "date": date.strftime("%Y-%m-%d"),
                "weekday": date.weekday(),
                "completions": 0,
                "total": 0,
                "status": "empty",  # empty, partial, complete
            }

        # Заполняем данные о выполнениях
        for comp in completions:
            day = comp.date.day
            if day in calendar_data:
                if comp.status == "completed":
                    calendar_data[day]["completions"] += 1
                calendar_data[day]["total"] += 1

        # Определяем статус для каждого дня
        for day, data in calendar_data.items():
            if data["total"] > 0:
                if data["completions"] == data["total"]:
                    data["status"] = "complete"
                elif data["completions"] > 0:
                    data["status"] = "partial"

        return {"month": month, "year": year, "calendar": list(calendar_data.values())}

    except Exception as e:
        logger.error(f"Ошибка при получении календаря привычек: {e}")
        return None
