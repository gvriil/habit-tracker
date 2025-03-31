# conftest.py
import os
import django
from django.conf import settings

# Настройка Django до запуска тестов
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()