from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelegramStateViewSet, NotificationLogViewSet, send_test_notification

router = DefaultRouter()
router.register(r'states', TelegramStateViewSet)
router.register(r'logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('', include(router.urls)),
    path('test-notification/', send_test_notification, name='test-notification'),
]