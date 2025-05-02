import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from telegram_bot.utils.logging import bot_logger
from .models import TelegramState, NotificationLog
from .serializers import TelegramStateSerializer, NotificationLogSerializer


def index(request):
    """Главная страница приложения с кнопкой для запуска бота."""
    return render(request, "telegram_bot/index.html")


# Замена стандартного логгера на специализированный
logger = bot_logger


def debug_request(view_func):
    """Декоратор для отладки HTTP запросов"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger.debug(f"====== НАЧАЛО ЗАПРОСА {request.path} ======")
        logger.debug(f"Метод: {request.method}")
        logger.debug(f"Заголовки: {request.headers}")

        if request.body:
            try:
                body = json.loads(request.body)
                logger.debug(
                    f"Тело запроса: {json.dumps(body, ensure_ascii=False, indent=2)}"
                )
            except:
                logger.debug(f"Тело запроса (raw): {request.body[:500]}")

        response = view_func(request, *args, **kwargs)

        logger.debug(f"Ответ: {response.status_code}")
        logger.debug(f"====== КОНЕЦ ЗАПРОСА {request.path} ======")
        return response

    return wrapper


def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram с логированием"""
    from django.conf import settings
    import requests

    bot_api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}"

    logger.debug(f"Отправка сообщения в Telegram: chat_id={chat_id}, text={text}")

    try:
        response = requests.post(
            f"{bot_api_url}/sendMessage", json={"chat_id": chat_id, "text": text}
        )

        if response.status_code == 200:
            logger.debug(f"Сообщение успешно отправлено: {response.json()}")
            return True
        else:
            logger.error(
                f"Ошибка отправки сообщения: {response.status_code}, {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Исключение при отправке сообщения: {e}")
        return False


@csrf_exempt
@require_POST
@debug_request
def telegram_webhook_view(request):
    """
    Обработчик вебхуков от Telegram API.

    Принимает входящие сообщения от Telegram и обрабатывает их.
    URL: /telegram-webhook/
    """
    bot_logger.info("=== ПОЛУЧЕН ЗАПРОС ОТ TELEGRAM ===")
    body = request.body.decode("utf-8")
    bot_logger.info(f"Тело запроса: {body}")
    logger.info("Получен запрос от Telegram: %s", request.body.decode("utf-8"))

    try:
        data = json.loads(request.body)

        # Логируем детали запроса для отладки
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        logger.info(f"Получено сообщение: chat_id={chat_id}, text={text}")

        # Проверяем тип сообщения
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]

            # Обработка команд
            if "text" in message:
                text = message["text"]

                # Обработка команды /start
                if text.startswith("/start"):
                    welcome_text = ("Привет! Я бот Habit Tracker. Чтобы связать аккаунт, "
                                    "используйте команду /connect <токен>")
                    send_telegram_message(chat_id, welcome_text)

                # Обработка команды /connect для привязки аккаунта
                elif text.startswith("/connect"):
                    try:
                        # Извлекаем токен
                        parts = text.split()
                        if len(parts) != 2:
                            raise ValueError("Неверный формат команды")

                        token = parts[1]
                        logger.debug(
                            f"Попытка связать аккаунт с токеном: {token[:5]}..."
                        )

                        # Найти пользователя по токену и связать его с chat_id
                        from users.models import User

                        user = User.objects.filter(auth_token=token).first()

                        if user:
                            user.telegram_id = chat_id
                            user.telegram_notifications = True
                            user.save()
                            logger.debug(
                                f"Аккаунт пользователя {user.id} связан с Telegram ID {chat_id}"
                            )

                            send_telegram_message(
                                chat_id,
                                f"Аккаунт успешно связан с Telegram! Теперь вы будете получать"
                                f" уведомления.",
                            )
                        else:
                            logger.warning(f"Токен не найден: {token[:5]}...")
                            send_telegram_message(
                                chat_id,
                                "Токен не найден. Пожалуйста, проверьте токен и попробуйте"
                                " снова.",
                            )
                    except Exception as e:
                        logger.error(f"Ошибка при обработке команды connect: {str(e)}")
                        send_telegram_message(
                            chat_id,
                            "Произошла ошибка при связывании аккаунта. Пожалуйста, попробуйте"
                            " ��озже.",
                        )

                # Добавляем отладочную команду
                elif text.startswith("/debug"):
                    # Отправляем отладочную информацию
                    from django.conf import settings

                    debug_info = "Отладочная информация:\n"
                    debug_info += f"- Telegram ID: {chat_id}\n"
                    debug_info += f"- Webhook URL: {settings.TELEGRAM_WEBHOOK_URL}\n"

                    # Проверка связанного аккаунта
                    from users.models import User

                    user = User.objects.filter(telegram_id=chat_id).first()
                    if user:
                        debug_info += f"- Связан с аккаунтом: {user.username}\n"
                    else:
                        debug_info += "- Аккаунт не связан\n"

                    send_telegram_message(chat_id, debug_info)

                # Другие команды или сообщения
                else:
                    send_telegram_message(
                        chat_id,
                        "Я не понимаю эту команду. Доступные команды: /start, /connect <токен>, /debug",
                    )

        return JsonResponse({"ok": True})

    except Exception as e:
        logger.error("Ошибка при обработке вебхука: %s", str(e), exc_info=True)
        return JsonResponse({"ok": False, "error": str(e)})


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def bot_debug_info(request):
    """
    Получение отладочной информации о боте.

    Возвращает текущее состояние бота, настройки вебхука и статистику сообщений.
    """
    from django.conf import settings
    import requests

    try:
        # Базовый URL для Telegram Bot API
        bot_api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}"

        # Получение информации о вебхуке
        webhook_info = requests.get(f"{bot_api_url}/getWebhookInfo").json()

        # Получение информации о боте
        bot_info = requests.get(f"{bot_api_url}/getMe").json()

        # Статистика сообщений
        message_count = NotificationLog.objects.count()

        # Статистика пользователей с подключенным Telegram
        from users.models import User

        telegram_users = User.objects.exclude(telegram_id=None).count()

        debug_data = {
            "bot_info": bot_info,
            "webhook_info": webhook_info,
            "message_stats": {
                "total_messages": message_count,
                "telegram_users": telegram_users,
            },
        }

        return Response(debug_data)

    except Exception as e:
        logger.error(f"Ошибка при получении дебаг-информации: {str(e)}")
        return Response(
            {"error": f"Ошибка: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Оставляем остальные классы без изменений
class TelegramStateViewSet(viewsets.ModelViewSet):
    serializer_class = TelegramStateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TelegramState.objects.all()


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return NotificationLog.objects.all()
        return NotificationLog.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def send_test_notification(request):
    user = request.user

    if not user.telegram_id or not user.telegram_notifications:
        return Response(
            {"error": "Необходимо подключить Telegram и включить уведомления"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Тестовое сообщение
        message = "Это тестовое уведомление от приложения Habit Tracker!"

        sent = send_telegram_message(user.telegram_id, message)

        # Логирование отправки
        NotificationLog.objects.create(
            user=user, habit=None, message=message, is_delivered=sent
        )

        if sent:
            return Response({"status": "Тестовое уведомление отправлено"})
        else:
            return Response(
                {"error": "Ошибка отправки уведомления"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        logger.error(f"Ошибка при отправке тестового уведомления: {str(e)}")
        return Response(
            {"error": f"Ошибка при отправке: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
