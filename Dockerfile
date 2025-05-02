# Базовый образ
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Копирование только файлов зависимостей
COPY pyproject.toml poetry.lock* ./
# Создание пустого README.md
RUN touch README.md

# Отключение создания виртуального окружения и установка без dev-зависимостей
RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi --no-root

# Важно: явная установка gunicorn через pip
RUN pip install gunicorn

# Копирование кода приложения
COPY . .