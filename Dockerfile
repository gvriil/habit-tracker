# Базовый образ для сборки
FROM python:3.11-slim AS builder

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копирование собранных пакетов из builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Установка пакетов из предварительно собранных wheels
RUN pip install --no-cache /wheels/*

# Копирование кода приложения
COPY . .

# Создание непривилегированного пользователя
RUN groupadd -r django && useradd -r -g django django && \
    chown -R django:django /app
RUN mkdir -p /var/log/gunicorn/ && \
    chown -R django:django /var/log/gunicorn/ && \
    chmod -R 775 /var/log/gunicorn/
USER django

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
