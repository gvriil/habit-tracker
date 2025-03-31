from rest_framework import serializers
from .models import Habit, HabitCompletion


class HabitSerializer(serializers.ModelSerializer):
    # Автоматически устанавливаем текущего пользователя при создании привычки
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Добавляем поле только для чтения, чтобы видеть имя пользователя в ответе
    user_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'name', 'description', 'place', 'action', 'user', 'user_name',
            'periodicity', 'time_to_complete', 'estimated_duration',
            'is_pleasant', 'is_public', 'related_habit',
            'reward', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

    def validate(self, data):
        """
        Проверка правил создания привычек:
        - Приятная привычка не может иметь вознаграждения или связанной привычки
        - Если указана связанная привычка, то не может быть указано вознаграждение
        - Связанная привычка должна быть приятной
        """
        is_pleasant = data.get('is_pleasant', False)
        related_habit = data.get('related_habit', None)
        reward = data.get('reward', None)

        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "Приятная привычка не может иметь вознаграждения или связанной привычки"
            )

        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя указать одновременно связанную привычку и вознаграждение"
            )

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной"
            )

        return data


class HabitCompletionSerializer(serializers.ModelSerializer):
    # Добавляем поле для получения информации о привычке
    habit_name = serializers.SerializerMethodField(read_only=True)

    # Добавляем поля, которые ожидаются тестами
    date_completed = serializers.DateTimeField(source='completed_at', read_only=True)
    time_completed = serializers.SerializerMethodField(read_only=True)
    is_successful = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = HabitCompletion
        fields = [
            'id', 'habit', 'habit_name', 'date_completed', 'time_completed',
            'is_successful', 'notes'
        ]

    def get_habit_name(self, obj):
        return obj.habit.name if obj.habit else None

    def get_time_completed(self, obj):
        if obj.completed_at:
            return obj.completed_at.strftime('%H:%M')
        return None

    def validate(self, data):
        # Дополнительная валидация по необходимости
        request = self.context.get('request')
        if request and request.user and data.get('habit'):
            # Проверяем, что пользователь отмечает выполнение только своих привычек
            if data['habit'].user != request.user:
                raise serializers.ValidationError("Можно отмечать только свои привычки")

        return data