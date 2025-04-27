import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

if __name__ == "__main__":
    from telegram_bot.bot import main
    asyncio.run(main())