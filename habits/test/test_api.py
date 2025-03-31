from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from habits.models import Habit, HabitCompletion
from habits.serializers import HabitSerializer, HabitCompletionSerializer

User = get_user_model()


class HabitAPITests(APITestCase):
    def setUp(self):
        # Создание тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # Создание тестовой привычки
        self.habit = Habit.objects.create(
            user=self.user,
            name='Утренняя зарядка',
            place='Дома',
            action='Делать упражнения',
            periodicity=1,
            estimated_duration=5,
            is_public=True,
            time_to_complete='08:00'
        )

        # Аутентификация для клиента API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # URL для тестирования
        self.list_url = reverse('habit-list')
        self.detail_url = reverse('habit-detail', args=[self.habit.id])

    def test_get_habit_list(self):
        """Тест получения списка привычек"""
        response = self.client.get(self.list_url)
        habits = Habit.objects.filter(user=self.user)
        serializer = HabitSerializer(habits, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_habit_detail(self):
        """Тест получения деталей привычки"""
        response = self.client.get(self.detail_url)

        # Проверяем отдельные важные поля вместо всего объекта
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.habit.name)
        self.assertEqual(response.data['place'], self.habit.place)
        self.assertEqual(response.data['action'], self.habit.action)

    def test_create_habit(self):
        """Тест создания привычки через API"""
        data = {
            'name': 'Новая привычка',
            'place': 'На работе',
            'action': 'Пить воду',
            'periodicity': 1,
            'estimated_duration': 1,
            'is_public': False,
            'time_to_complete': '12:00'
        }

        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что привычка действительно создана
        self.assertTrue(Habit.objects.filter(name='Новая привычка').exists())

    def test_update_habit(self):
        """Тест обновления привычки через API"""
        data = {
            'name': 'Обновленная привычка',
            'place': self.habit.place,
            'action': self.habit.action,
            'periodicity': self.habit.periodicity,
            'estimated_duration': self.habit.estimated_duration,
        }

        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка обновленного значения
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.name, 'Обновленная привычка')

    def test_delete_habit(self):
        """Тест удаления привычки через API"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверка, что привычка удалена
        self.assertFalse(Habit.objects.filter(id=self.habit.id).exists())

    def test_public_habit_list(self):
        """Тест получения списка публичных привычек"""
        # Создаем еще одну публичную привычку
        Habit.objects.create(
            user=self.user,
            name='Еще одна публичная привычка',
            place='Везде',
            action='Что-то делать',
            periodicity=1,
            estimated_duration=5,
            is_public=True,
            time_to_complete='09:00'  # Добавляем обязательное поле
        )

        url = reverse('public-habit-list')
        response = self.client.get(url)

        # Проверяем только кол-во и статус
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class HabitCompletionAPITests(APITestCase):
    def setUp(self):
        # Создание пользователя и привычки
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Тестовая привычка',
            place='Дом',
            action='Действие',
            periodicity=1,
            estimated_duration=5,
            time_to_complete='08:00'  # Добавляем обязательное поле
        )

        # Аутентификация
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # URL для тестирования
        self.completion_url = reverse('habit-completion-list')

    def test_mark_habit_as_complete(self):
        """Тест отметки о выполнении привычки"""
        data = {'habit': self.habit.id}

        url = reverse('habit-completion-list')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(HabitCompletion.objects.filter(
            habit=self.habit,
            user=self.user
        ).exists())

    def test_get_habit_completions(self):
        """Тест получения истории выполнения привычки"""
        # Создаем несколько записей о выполнении
        HabitCompletion.objects.create(habit=self.habit, user=self.user)
        HabitCompletion.objects.create(habit=self.habit, user=self.user)
        
        url = reverse('habit-completion-list', args=[self.habit.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)