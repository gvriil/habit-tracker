import os

import django
import pytest
from django.core.management import call_command


# Настройка Django до запуска тестов
def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Применяем миграции перед запуском тестов
        call_command("migrate")
