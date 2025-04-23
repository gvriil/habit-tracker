from django.core.management.base import BaseCommand
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Настройка вебхука для Telegram бота'

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN

        # Получаем текущую информацию о вебхуке
        info_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(info_url)
        self.stdout.write(f"Текущий статус вебхука: {response.json()}")

        # Устанавливаем новый вебхук
        webhook_url = "https://ad1a-142-132-140-123.ngrok-free.app/telegram-webhook/"
        set_url = f"https://api.telegram.org/bot{token}/setWebhook"
        data = {"url": webhook_url}
        response = requests.post(set_url, data=data)
        self.stdout.write(f"Установка вебхука: {response.json()}")