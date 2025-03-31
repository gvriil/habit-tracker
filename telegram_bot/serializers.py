from rest_framework import serializers
from .models import TelegramState, NotificationLog


class TelegramStateSerializer(serializers.ModelSerializer):
    """Сериализатор для состояния диалога в Telegram."""

    class Meta:
        model = TelegramState
        fields = ['id', 'user', 'telegram_id', 'state', 'context', 'updated_at']
        read_only_fields = ['updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Сериализатор для логов уведомлений."""
    habit_name = serializers.CharField(source='habit.name', read_only=True)

    class Meta:
        model = NotificationLog
        fields = ['id', 'user', 'habit', 'habit_name', 'sent_at', 'message', 'is_delivered']
        read_only_fields = ['sent_at']