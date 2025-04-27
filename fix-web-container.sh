#!/bin/bash
docker-compose down
# Добавляем gunicorn в зависимости
sed -i 's/^RUN pip install --no-cache-dir -r requirements.txt$/RUN pip install --no-cache-dir -r requirements.txt gunicorn/' ~/habit-tracker/Dockerfile
docker-compose build web
docker-compose up -d
