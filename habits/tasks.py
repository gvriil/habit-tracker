import os
import logging
from datetime import datetime, timedelta

from telegram import Bot, ParseMode
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q

from habits.models import Habit, HabitCompletion
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger(__name__)

load_dotenv()

# Загрузка токена бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


@shared_task
def send_habit_reminders():
    """Отправка напоминаний о привычках, которые нужно выполнить в ближайшее время."""
    now = timezone.now()
    current_time = now.time()

    # Проверяем привычки, время которых в ближайшие 30 минут
    time_threshold = (now + timedelta(minutes=30)).time()

    # Особый случай: если текущее время например 23:45, а time_threshold будет 00:15
    if current_time > time_threshold:
        habits_to_remind = Habit.objects.filter(
            time_to_complete__gte=current_time
        ) | Habit.objects.filter(
            time_to_complete__lte=time_threshold
        )
    else:
        habits_to_remind = Habit.objects.filter(
            time_to_complete__gte=current_time,
            time_to_complete__lte=time_threshold
        )

    # Исключаем привычки, которые уже выполнены сегодня
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    count = 0
    for habit in habits_to_remind:
        # Проверяем, выполнена ли привычка сегодня
        is_completed_today = HabitCompletion.objects.filter(
            habit=habit,
            completed_at__gte=today_start
        ).exists()

        if not is_completed_today:
            # Используем .delay() для асинхронного вызова
            send_habit_reminder.delay(habit.id)
            count += 1

    logger.info(f"Запланировано {count} напоминаний о привычках")
    return count


@shared_task
def send_habit_reminder(habit_id):
    """Отправка напоминания о конкретной привычке."""
    try:
        # Получаем привычку из базы по ID для предотвращения ошибок сериализации
        habit = Habit.objects.get(id=habit_id)
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        # Импортируем здесь для предотвращения циклического импорта
        from telegram_bot import user_data

        user_id = habit.user_id
        telegram_chat_id = None

        # Поиск telegram_chat_id для пользователя
        for chat_id, data in user_data.items():
            if data.get('user_id') == user_id:
                telegram_chat_id = chat_id
                break

        if telegram_chat_id:
            # Формируем текст напоминания
            reminder_text = format_habit_reminder(habit)

            try:
                # Отправляем напоминание с поддержкой Markdown
                bot.send_message(
                    chat_id=telegram_chat_id,
                    text=reminder_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(
                    f"Отправлено напоминание для привычки {habit.name} пользователю {user_id}")
                return True
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания: {e}")
                return False
        else:
            logger.warning(f"Не найден telegram_chat_id для пользователя {user_id}")
            return False
    except Habit.DoesNotExist:
        logger.error(f"Привычка с ID {habit_id} не найдена")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке напоминания: {e}")
        return False


@shared_task
def schedule_reminder(habit_id, minutes_before=30):
    """Планирует напоминание за определенное количество минут до события"""
    try:
        habit = Habit.objects.get(id=habit_id)

        # Получаем время напоминания
        now = timezone.now()
        reminder_time = now + timedelta(minutes=minutes_before)

        # Планируем задачу
        send_habit_reminder.apply_async(
            args=[habit_id],
            eta=reminder_time
        )
        return True  # Важно вернуть True при успешном выполнении
    except Exception as e:
        logger.error(f"Ошибка планирования напоминания: {e}")
        return False


@shared_task
def schedule_weekly_reminders():
    """Планирует напоминания для всех привычек на неделю вперед"""
    habits = Habit.objects.filter(is_active=True)
    scheduled = 0

    for habit in habits:
        if schedule_reminder(habit.id):
            scheduled += 1

    logger.info(f"Запланировано {scheduled} напоминаний на неделю")
    return scheduled


def format_habit_reminder(habit):
    """Формирование текста напоминания о привычке."""
    message = f"⏰ *НАПОМИНАНИЕ*\n\n"
    message += f"Пора выполнить привычку: *{habit.name}*\n"

    # Обработка времени выполнения с проверкой типа данных
    if habit.time_to_complete:
        try:
            # Если это объект datetime/time, используем strftime
            time_str = habit.time_to_complete.strftime('%H:%M')
        except (AttributeError, TypeError):
            # Если это строка или другой тип, используем как есть
            time_str = habit.time_to_complete
        message += f"Время: {time_str}\n"

    if habit.place:
        message += f"Место: {habit.place}\n"

    if habit.action:
        message += f"Действие: {habit.action}\n"

    message += f"Продолжительность: {habit.estimated_duration} минут\n\n"

    # Добавляем информацию о связанных привычках или наградах
    if hasattr(habit, 'related_habit') and habit.related_habit:
        message += f"После выполнения вы можете: _{habit.related_habit.name}_\n"
    elif hasattr(habit, 'reward') and habit.reward:
        message += f"Ваша награда: _{habit.reward}_\n"

    # Добавляем информацию о прогрессе
    completions_count = HabitCompletion.objects.filter(habit=habit).count()
    if completions_count > 0:
        message += f"\nВы выполнили эту привычку {completions_count} раз!\n"

    message += "\nНе забудьте отметить выполнение в боте командой /complete"

    return message


@shared_task
def send_daily_statistics(user_id):
    """Отправка ежедневной статистики выполнения привычек"""
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Получаем привычки пользователя
        habits = Habit.objects.filter(user_id=user_id)
        total_habits = habits.count()

        # Получаем выполненные вчера привычки
        completed_yesterday = HabitCompletion.objects.filter(
            habit__user_id=user_id,
            completed_at__date=yesterday
        ).values('habit').distinct().count()

        # Процент выполнения
        completion_percentage = (
                    completed_yesterday / total_habits * 100) if total_habits > 0 else 0

        # Импортируем здесь для предотвращения циклического импорта
        from telegram_bot import user_data

        telegram_chat_id = None
        # Поиск telegram_chat_id для пользователя
        for chat_id, data in user_data.items():
            if data.get('user_id') == user_id:
                telegram_chat_id = chat_id
                break

        if telegram_chat_id:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)

            message = f"📊 *Статистика за {yesterday.strftime('%d.%m.%Y')}*\n\n"
            message += f"Всего привычек: {total_habits}\n"
            message += f"Выполнено вчера: {completed_yesterday}\n"
            message += f"Процент выполнения: {completion_percentage:.1f}%\n\n"

            if completion_percentage >= 80:
                message += "🎉 Отличная работа! Продолжайте в том же духе!"
            elif completion_percentage >= 50:
                message += "👍 Хороший результат! Стремитесь к большему!"
            else:
                message += "💪 Не сдавайтесь! Маленькие шаги приводят к большим результатам!"

            bot.send_message(
                chat_id=telegram_chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        else:
            logger.warning(f"Не найден telegram_chat_id для пользователя {user_id}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при отправке статистики: {e}")
        return False


def get_chat_id_by_user(user_id):
    """
    Получить chat_id пользователя Telegram по ID пользователя Django.
    """
    # Импортируем здесь для предотвращения циклического импорта
    from telegram_bot import user_data

    telegram_chat_id = None
    # Поиск telegram_chat_id для пользователя
    for chat_id, data in user_data.items():
        if data.get('user_id') == user_id:
            telegram_chat_id = chat_id
            break

    return telegram_chat_id