from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Сериализатор для создания пользователей через Djoser."""
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'password2',
                  'telegram_id', 'telegram_username')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password2', None)
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'telegram_id', 'telegram_username',
                  'notify_before_minutes', 'telegram_notifications')
        read_only_fields = ('id',)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления данных пользователя без пароля."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'telegram_id', 'telegram_username',
                  'notify_before_minutes', 'telegram_notifications')
        read_only_fields = ('id',)
