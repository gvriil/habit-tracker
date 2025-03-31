# token_management/management/commands/save_token.py
import json
from django.core.management.base import BaseCommand
from token_management.services import TokenService


class Command(BaseCommand):
    help = 'Сохраняет JWT токен для пользователя'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID пользователя')
        parser.add_argument('token_file', type=str, help='Путь к файлу с токеном')

    def handle(self, *args, **kwargs):
        user_id = kwargs['user_id']
        token_file = kwargs['token_file']

        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)

            token_service = TokenService()

            if 'access' in token_data:
                token_service.store_user_token(user_id, token_data['access'], 'access')
                self.stdout.write(
                    self.style.SUCCESS(f'Access токен сохранен для пользователя {user_id}'))

            if 'refresh' in token_data:
                token_service.store_user_token(user_id, token_data['refresh'], 'refresh')
                self.stdout.write(
                    self.style.SUCCESS(f'Refresh токен сохранен для пользователя {user_id}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка сохранения токена: {str(e)}'))