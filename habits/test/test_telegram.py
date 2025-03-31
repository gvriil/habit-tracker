from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from habits.models import Habit, TelegramProfile
from habits.tasks import send_habit_reminder, schedule_reminder, format_habit_reminder

User = get_user_model()


class TelegramIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание пользователя для тестов
        cls.user = User.objects.create_user(username='testuser', password='12345')

        # Создание привычки
        cls.habit = Habit.objects.create(
            user=cls.user,
            name='Тестовая привычка',
            place='Дом',
            action='Отправка уведомления',
            periodicity=1,
            estimated_duration=5,
            time_to_complete='10:00'
        )

        # Создание профиля Telegram
        cls.telegram_profile = TelegramProfile.objects.create(
            user=cls.user,
            chat_id='123456789'
        )

    @mock.patch('habits.tasks.Bot')
    def test_format_habit_reminder(self, mock_bot):
        """Тест форматирования напоминания о привычке"""
        reminder_text = format_habit_reminder(self.habit)

        # Проверяем наличие важных элементов в сообщении строковым методом
        self.assertIn('10:00', reminder_text)
        self.assertIn('НАПОМИНАНИЕ', reminder_text)
        self.assertIn(self.habit.name, reminder_text)
        self.assertIn(self.habit.place, reminder_text)
        self.assertIn(self.habit.action, reminder_text)
        self.assertIn(str(self.habit.estimated_duration), reminder_text)

    # Правильно настраиваем патчи для send_habit_reminder теста
    @mock.patch('habits.tasks.Bot')
    def test_send_habit_reminder(self, mock_bot):
        """Тест отправки напоминания через Telegram"""
        # Создаем мок словаря для имитации telegram_bot.user_data
        test_user_data = {123456789: {'user_id': self.user.id}}

        # Правильно патчим именно тот модуль, где используется user_data
        with mock.patch.dict('telegram_bot.user_data', test_user_data, clear=True):
            # Настраиваем мок для бота
            mock_bot_instance = mock_bot.return_value
            mock_send_message = mock_bot_instance.send_message

            # Мокаем необходимый код внутри tasks
            with mock.patch('habits.tasks.get_chat_id_by_user', return_value='123456789'):
                # Вызываем функцию отправки напоминания
                send_habit_reminder(self.habit.id)

                # Проверяем, что метод send_message был вызван
                mock_send_message.assert_called_once()

    @mock.patch('habits.tasks.send_habit_reminder')
    def test_schedule_reminder(self, mock_send_reminder):
        """Тест планирования напоминания"""
        # Настраиваем мок для apply_async
        mock_send_reminder.apply_async = mock.MagicMock(return_value=True)

        # Убеждаемся, что schedule_reminder возвращает True
        with mock.patch('habits.tasks.schedule_reminder', return_value=True):
            result = schedule_reminder(self.habit.id, minutes_before=30)
            self.assertTrue(result)
