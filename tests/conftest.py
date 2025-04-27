# tests/conftest.py
import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Заменяет соединение с БД на SQLite in-memory для тестов."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
