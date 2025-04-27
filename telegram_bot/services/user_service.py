from datetime import timedelta
from typing import Dict, Optional, Any, List

from asgiref.sync import sync_to_async
from django.apps import apps
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.utils import timezone

# Настройка логгера
from telegram_bot.utils.logging import bot_logger

logger = bot_logger

# Константы для кэширования
USER_CACHE_PREFIX = "tg_user_"
USER_SESSION_PREFIX = "tg_session_"
USER_ACTIVITY_PREFIX = "tg_activity_"
CACHE_TIMEOUT = 60 * 30  # 30 минут
SESSION_TIMEOUT = 60 * 60 * 24 * 7  # 7 дней


class UserDataManager:
    """Класс для управления данными пользователей с оптимизацией запросов и кэшированием"""

    @staticmethod
    def get_cache_key(prefix: str, user_id: int) -> str:
        """Генерация ключа кэша для пользователя"""
        return f"{prefix}{user_id}"

    @staticmethod
    async def get_user(telegram_id: int) -> Optional[Dict]:
        """Получение данных пользователя с использованием кэша"""
        cache_key = UserDataManager.get_cache_key(USER_CACHE_PREFIX, telegram_id)

        # Пробуем получить из кэша
        user_data = cache.get(cache_key)
        if user_data:
            return user_data

        # Если нет в кэше, загружаем из БД
        user = await UserDataManager._load_user_from_db(telegram_id)
        if user:
            # Сохраняем в кэш
            user_data = {
                'id': user.id,
                'username': user.username,
                'telegram_id': user.telegram_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'telegram_notifications': user.telegram_notifications,
                'last_active': str(user.last_activity) if user.last_activity else None
            }
            cache.set(cache_key, user_data, CACHE_TIMEOUT)
            return user_data
        return None

    @staticmethod
    @sync_to_async
    def _load_user_from_db(telegram_id: int) -> Optional[Any]:
        """Загрузка пользователя из базы данных с оптимизацией запроса"""
        User = apps.get_model('users', 'User')
        try:
            return User.objects.filter(telegram_id=telegram_id).first()
        except Exception as e:
            logger.error(f"Ошибка при загрузке пользователя {telegram_id}: {e}")
            return None

    @staticmethod
    async def update_activity(telegram_id: int) -> bool:
        """Обновление данных об активности пользователя"""
        try:
            User = apps.get_model('users', 'User')

            # Кэшируем активность, чтобы не обновлять БД при каждом запросе
            activity_key = UserDataManager.get_cache_key(USER_ACTIVITY_PREFIX, telegram_id)
            last_update = cache.get(activity_key)

            now = timezone.now()

            # Обновляем БД только если прошло больше 5 минут с последнего обновления
            if not last_update or (now - last_update).total_seconds() > 300:
                await sync_to_async(User.objects.filter(telegram_id=telegram_id).update)(
                    last_activity=now
                )
                cache.set(activity_key, now, CACHE_TIMEOUT)
                logger.debug(f"Обновлена активность для пользователя {telegram_id}")

            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении активности пользователя {telegram_id}: {e}")
            return False

    @staticmethod
    async def get_user_habits(telegram_id: int) -> List[Dict]:
        """Получение привычек пользователя с оптимизированным запросом"""
        habits_key = f"tg_habits_{telegram_id}"

        # Пробуем получить из кэша
        cached_habits = cache.get(habits_key)
        if cached_habits:
            return cached_habits

        # Если нет в кэше, загружаем из БД
        try:
            Habit = apps.get_model('habits', 'Habit')
            HabitCompletion = apps.get_model('habits', 'HabitCompletion')
            User = apps.get_model('users', 'User')

            # Используем select_related и prefetch_related для оптимизации
            user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
            if not user:
                return []

            # Оптимизированный запрос с предзагрузкой связанных данных
            habits = await sync_to_async(
                lambda: list(Habit.objects.filter(user=user)
                .prefetch_related(
                    Prefetch('habitcompletion_set',
                             queryset=HabitCompletion.objects.order_by('-date'))
                ))
            )()

            # Импортируем внутри функции чтобы избежать циклических импортов
            from telegram_bot.services.habits import calculate_streak

            result = []
            for habit in habits:
                # Получаем серию выполнений
                streak = await sync_to_async(calculate_streak)(habit)

                result.append({
                    'id': habit.id,
                    'name': habit.name,
                    'category': habit.category,
                    'time_of_day': habit.time_of_day,
                    'frequency': habit.frequency,
                    'streak': streak,
                })

            # Сохраняем в кэш на короткое время
            cache.set(habits_key, result, 60 * 5)  # 5 минут
            return result

        except Exception as e:
            logger.error(f"Ошибка при получении привычек пользователя {telegram_id}: {e}")
            return []

    @staticmethod
    async def clear_user_cache(telegram_id: int) -> None:
        """Очистка всего кэша для пользователя"""
        keys = [
            UserDataManager.get_cache_key(USER_CACHE_PREFIX, telegram_id),
            UserDataManager.get_cache_key(USER_SESSION_PREFIX, telegram_id),
            UserDataManager.get_cache_key(USER_ACTIVITY_PREFIX, telegram_id),
            f"tg_habits_{telegram_id}"
        ]
        for key in keys:
            cache.delete(key)


class SessionManager:
    """Класс для управления пользовательскими сессиями"""

    @staticmethod
    async def set_session_data(telegram_id: int, key: str, value: Any) -> None:
        """Сохранение данных сессии"""
        session_key = UserDataManager.get_cache_key(USER_SESSION_PREFIX, telegram_id)
        session = cache.get(session_key) or {}
        session[key] = value
        cache.set(session_key, session, SESSION_TIMEOUT)

    @staticmethod
    async def get_session_data(telegram_id: int, key: str) -> Optional[Any]:
        """Получение данных сессии"""
        session_key = UserDataManager.get_cache_key(USER_SESSION_PREFIX, telegram_id)
        session = cache.get(session_key) or {}
        return session.get(key)

    @staticmethod
    async def clear_session(telegram_id: int) -> None:
        """Очистка сессии пользователя"""
        session_key = UserDataManager.get_cache_key(USER_SESSION_PREFIX, telegram_id)
        cache.delete(session_key)

    @staticmethod
    @sync_to_async
    def cleanup_old_sessions() -> int:
        """Очистка устаревших сессий в БД"""
        TelegramState = apps.get_model('telegram_bot', 'TelegramState')
        cutoff_date = timezone.now() - timedelta(days=7)

        # Находим и удаляем старые записи о состояниях
        old_records = TelegramState.objects.filter(updated_at__lt=cutoff_date)
        count = old_records.count()
        old_records.delete()

        logger.info(f"Удалено {count} устаревших записей о состояниях Telegram")
        return count


async def get_active_users(days: int = 7) -> List[Dict]:
    """Получение списка активных пользователей за последние дни"""
    User = apps.get_model('users', 'User')

    cutoff_date = timezone.now() - timedelta(days=days)

    active_users = await sync_to_async(
        lambda: list(User.objects.filter(
            Q(last_activity__gt=cutoff_date) | Q(last_login__gt=cutoff_date),
            telegram_id__isnull=False
        ).values('id', 'username', 'telegram_id', 'last_activity', 'last_login'))
    )()

    return active_users


# Инициализация глобального менеджера данных пользователей
user_data = UserDataManager()
session_manager = SessionManager()
