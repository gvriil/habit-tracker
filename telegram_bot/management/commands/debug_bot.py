from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json


class Command(BaseCommand):
    help = 'Проверка настройки вебхука и статуса бота'

    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        api_url = f"https://api.telegram.org/bot{bot_token}"

        # Проверка вебхука
        webhook_info = requests.get(f"{api_url}/getWebhookInfo").json()
        self.stdout.write("Информация о вебхуке:")
        self.stdout.write(json.dumps(webhook_info, indent=2, ensure_ascii=False))

        # Проверка доступности бота
        bot_info = requests.get(f"{api_url}/getMe").json()
        self.stdout.write("\nИнформация о боте:")
        self.stdout.write(json.dumps(bot_info, indent=2, ensure_ascii=False))

        # Проверка настроенного URL
        self.stdout.write(f"\nНастроенный URL: {settings.TELEGRAM_WEBHOOK_URL}")

        # Рекомендация по исправлению проблемы
        if webhook_info.get("result", {}).get("url") != settings.TELEGRAM_WEBHOOK_URL:
            self.stdout.write(self.style.WARNING(
                f"Текущий вебхук отличается от настроенного! Запустите команду setup_webhook."))