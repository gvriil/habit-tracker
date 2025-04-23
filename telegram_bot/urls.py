from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import telegram_webhook_view, bot_debug_info

from .views import TelegramStateViewSet, NotificationLogViewSet, send_test_notification

router = DefaultRouter()
router.register(r'states', TelegramStateViewSet)
router.register(r'logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('telegram-webhook/', telegram_webhook_view, name='telegram_webhook'),

    path('bot-debug/', bot_debug_info, name='bot_debug'),

    path('', include(router.urls)),
    path('test-notification/', send_test_notification, name='test-notification'),
]