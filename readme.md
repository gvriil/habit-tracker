# Habit Tracker - Система отслеживания полезных привычек

## Описание проекта

Habit Tracker - это веб-приложение, предназначенное для отслеживания и формирования полезных привычек. Система помогает пользователям создавать, отслеживать и поддерживать привычки, а также получать уведомления о необходимости их выполнения.

### Основные возможности

- Создание и управление привычками
- Установка периодичности выполнения
- Связывание привычек (создание цепочек)
- Публичные и приватные привычки
- Система вознаграждений
- Уведомления через Telegram
- Трекинг прогресса

## Технический стек

- **Backend**: Django, Django REST Framework
- **База данных**: PostgreSQL
- **Интеграции**: Telegram Bot API
- **Документация API**: Swagger/ReDoc (drf-yasg)
- **Тестирование**: Django Test Framework

## Требования к системе

- Python 3.8+
- PostgreSQL 12+
- Redis (для Celery)

## Установка и локальный запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/your_username/habit_tracker.git
cd habit_tracker
```
### 2. Создание и активация виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate  # Для Windows
```

```bash
pip install -r requirements.txt
```
### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
#### Создайте файл .env в корневой директории проекта и заполните его:

```bash
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=habit_tracker
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 5. Применение миграций

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash 
python manage.py createsuperuser
```

### 7. Запуск проекта

```bash
python manage.py runserver
```

### 8. Запуск Celery worker для фоновых задач

```bash
celery -A config worker -l info
```

### 9. Запуск Celery Beat для регулярных задач (отдельный терминал)

```bash
celery -A config beat -l info
```

### Структура API

#### API доступен по адресу /api/ и включает следующие основные эндпоинты:  
- /api/habits/ - CRUD операции с привычками
- /api/habits/{id}/complete/ - Отметка привычки как выполненной
- /api/habits/my_habits/ - Просмотр только своих привычек
- /api/public_habits/ - Просмотр публичных привычек
- /api/telegram/test_notification/ - Отправка тестового уведомления

### Документация API

#### Документация API доступна по следующим URL:  
- /swagger/ - интерфейс Swagger UI
- /redoc/ - интерфейс ReDoc
- /swagger.json - документация в формате JSON
- /swagger.yaml - документация в формате YAML

### Проверка соответствия требованиям ТЗ

#### Функциональные требования

- ✅ Создание, просмотр, редактирование и удаление привычек 
- ✅ Просмотр чужих привычек (только публичных) 
- ✅ Возможность задавать периодичность (не реже раза в 7 дней) 
- ✅ Время на выполнение привычки не больше 120 секунд 
- ✅ Указание связанных привычек или вознаграждений (но не вместе) 
- ✅ Связанными могут быть только привычки с признаком "приятная привычка" 
- ✅ У приятной привычки не может быть вознаграждения или связанной привычки 
- ✅ Валидация данных на уровне моделей и сериализаторов  

#### Технические требования

- ✅ Настроен CORS для работы с фронтендом 
- ✅ Документация API через Swagger/ReDoc 
- ✅ Система уведомлений через Telegram Bot 
- ✅ Настроены периодические задачи через Celery 
- ✅ Кастомная админ-панель Django 
- ✅ Тесты для проверки работы API 
- ✅ Размещение проекта на сервере  


### Лицензия

#### MIT License




## Настройка и запуск Telegram-бота

Для работы с Telegram-ботом выполните следующие шаги:

### Предварительная настройка
1. Создайте бота в Telegram через [@BotFather](https://t.me/BotFather)
2. Получите токен и добавьте его в файл `.env` в параметре `TELEGRAM_BOT_TOKEN`

### Запуск сервисов
Для корректной работы бота необходимо запустить следующие компоненты:

1. **Django-сервер**
```bash
source venv/bin/activate
python manage.py runserver 
"url=https://your-domain.com/api/telegram/webhook/"https://api.telegram.org/botTOKEN/setWebhook
```
### Celery worker (для обработки задач)

```bash
source venv/bin/activate
celery -A config worker -l info
```

### Telegram-бот

```bash
source venv/bin/activate
python telegram_bot.py
```

#### Использование бота
- Откройте бота в Telegram
- Отправьте команду /start для начала работы
- Следуйте инструкциям для аутентификации
- Используйте команду /help для просмотра доступных функций

## Возможные причины неработоспособности

1. Убедитесь, что Redis запущен для работы с Celery
2. Проверьте актуальность токена бота
3. Для локальной разработки рекомендуется использовать long polling (как сейчас у вас)

Эту информацию важно включить в README, чтобы облегчить развертывание и использование проекта.