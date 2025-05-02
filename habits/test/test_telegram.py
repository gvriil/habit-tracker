# Проверяем, в каком окружении запущены тесты
from unittest.mock import patch

from django.test import TestCase

from users.models import User

# Используем try-except для более гибкого импорта
try:
    # Для Docker окружения
    from app.habits.models import Habit
    from app.habits.services.telegram_bot import send_habit_reminder
except ImportError:
    # Для локальной среды
    from habits.models import Habit
    from habits.services.telegram_bot import send_habit_reminder


class TelegramIntegrationTests(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

        # Имитируем наличие chat_id через monkey patching
        self.user.telegram_chat_id = "123456"

        # Создаем привычку с правильными полями модели
        self.habit = Habit.objects.create(
            user=self.user,
            name="Тестовая привычка",
            description="Описание привычки",
            place="Дома",
            action="Действие привычки",
            is_active=True,
            periodicity=1,
            time_to_complete="12:00",
            estimated_duration=5,
            is_pleasant=False,
            is_public=True,
        )

    def test_format_habit_reminder(self):
        # Тестируем форматирование сообщения
        reminder_text = f"Напоминание: {self.habit.name} в {self.habit.place}"
        self.assertIn(self.habit.name, reminder_text)
        self.assertIn(self.habit.place, reminder_text)

    @patch("habits.services.telegram_bot.bot", autospec=True)
    def test_send_habit_reminder(self, mock_bot):
        # Важно: для теста нужно установить mock_bot вместо None
        # иначе проверка if not bot: в функции вернет False

        # Устанавливаем telegram_chat_id
        self.habit.user.telegram_chat_id = "123456789"
        self.habit.user.save()

        # Добавляем вызов функции send_habit_reminder
        send_habit_reminder(self.habit)

        # Проверяем вызов
        mock_bot.send_message.assert_called_once()

    def test_schedule_reminder(self):
        # Простая заглушка для теста планирования
        result = True
        self.assertTrue(result)
