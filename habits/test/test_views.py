from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit, HabitCompletion

User = get_user_model()


class HabitViewsTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.habit = Habit.objects.create(
            user=cls.user,
            name='Тестовая привычка',
            place='Дом',
            action='Делать отжимания',
            time_to_complete='09:00'
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_habit_detail_view(self):
        """Тест представления деталей привычки"""
        url = reverse('habit-detail', args=[self.habit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовая привычка')

    def test_habit_update_view(self):
        """Тест обновления привычки"""
        url = reverse('habit-detail', args=[self.habit.id])
        data = {'name': 'Обновленная привычка', 'place': 'Дом', 'action': 'Делать отжимания',
                'time_to_complete': '09:00'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.name, 'Обновленная привычка')

    def test_habit_delete_view(self):
        """Тест удаления привычки"""
        url = reverse('habit-detail', args=[self.habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=self.habit.id).count(), 0)

    def test_habit_completion_create(self):
        """Тест создания записи о выполнении привычки"""
        url = reverse('habit-completion-create')
        data = {'habit': self.habit.id, 'notes': 'Отличная работа!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HabitCompletion.objects.count(), 1)
