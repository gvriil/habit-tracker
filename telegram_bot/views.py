import logging

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import TelegramState, NotificationLog
from .serializers import TelegramStateSerializer, NotificationLogSerializer

logger = logging.getLogger(__name__)


class TelegramStateViewSet(viewsets.ModelViewSet):
    """
    API для управления состояниями диалога в Telegram.

    retrieve:
    Получение информации о конкретном состоянии диалога.

    list:
    Получение списка всех состояний диалогов в Telegram.

    create:
    Создание нового состояния диалога.

    update:
    Обновление состояния диалога.

    partial_update:
    Частичное обновление состояния диалога.

    destroy:
    Удаление состояния диалога.
    """
    serializer_class = TelegramStateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TelegramState.objects.all()


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра логов уведомлений (только чтение).

    retrieve:
    Получение информации о конкретном уведомлении.

    list:
    Получение списка всех уведомлений пользователя.
    Администратор видит все уведомления, обычные пользователи - только свои.
    """
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список уведомлений в зависимости от прав пользователя.

        Администратор видит все уведомления, обычные пользователи - только свои.
        """
        if self.request.user.is_superuser:
            return NotificationLog.objects.all()
        return NotificationLog.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_test_notification(request):
    """
    Отправить тестовое уведомление в Telegram.

    Проверяет возможность отправки уведомлений пользователю через Telegram.
    Пользователь должен быть авторизован и иметь подключенный Telegram
    с включенными уведомлениями.

    Returns:
        Response: Статус отправки уведомления или информацию об ошибке.
    """
    user = request.user

    if not user.telegram_id or not user.telegram_notifications:
        return Response(
            {"error": "Необходимо подключить Telegram и включить уведомления"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Тестовое сообщение
        message = "Это тестовое уведомление от приложения Habit Tracker!"

        # Логирование отправки
        NotificationLog.objects.create(
            user=user,
            habit=None,
            message=message,
            is_delivered=True
        )

        return Response({"status": "Тестовое уведомление отправлено"})

    except Exception as e:
        logger.error(f"Ошибка при отправке тестового уведомления: {str(e)}")
        return Response(
            {"error": f"Ошибка при отправке: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )