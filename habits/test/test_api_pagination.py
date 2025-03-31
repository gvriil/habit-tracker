from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from habits.models import Habit

User = get_user_model()

class HabitPaginationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем пользователя для тестов
        cls.user = User.objects.create_user(username='testuser', password='password')

        # Создаем 7 привычек
        for i in range(7):
            Habit.objects.create(
                user=cls.user,
                name=f'Test Habit {i}',
                place=f'Test Place {i}',
                time_to_complete='08:00:00',
                action=f'Test Action {i}',
                is_pleasant=i % 2 == 0,
                is_public=i % 3 == 0,
                periodicity=i + 1,
                estimated_duration=60
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_pagination_my_habits(self):
        """Проверяем, что на странице отображается 5 привычек"""
        url = reverse('my-habits')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_second_page_pagination(self):
        """Проверяем доступ ко второй странице"""
        url = reverse('my-habits')
        response = self.client.get(url, {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_filtering_by_is_pleasant(self):
        """Проверяем фильтрацию по приятным привычкам"""
        url = reverse('my-habits')
        response = self.client.get(url, {'is_pleasant': True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pleasant_habits = sum(1 for h in response.data['results'] if h['is_pleasant'])
        self.assertEqual(pleasant_habits, len(response.data['results']))

    def test_search_by_name(self):
        """Проверяем поиск по имени"""
        url = reverse('my-habits')
        response = self.client.get(url, {'search': 'Test Habit 1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all('Test Habit 1' in h['name'] for h in response.data['results']))