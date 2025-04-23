from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123',
            're_password': 'StrongPassword123'
        }
        self.login_data = {
            'username': 'testuser',
            'password': 'StrongPassword123'
        }

    def test_registration(self):
        """Тестирование регистрации пользователя."""
        url = '/api/auth/users/'
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_login_jwt(self):
        """Тестирование получения JWT-токена."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        url = '/api/auth/jwt/create/'
        credentials = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_login(self):
        """Тестирование неуспешной авторизации."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        invalid_credentials = {
            'username': self.user_data['username'],
            'password': 'WrongPassword'
        }

        url = '/api/auth/jwt/create/'
        response = self.client.post(url, invalid_credentials, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)  # Изменено с 400 на 401

    def test_access_protected_view(self):
        """Тестирование доступа к защищенному эндпоинту."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        url = '/api/auth/jwt/create/'
        credentials = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, credentials, format='json')
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        url = '/api/auth/users/me/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
