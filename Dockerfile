FROM python:3.10-slim

WORKDIR /app

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск приложения
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]