from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import (
    validate_execution_time,
    validate_periodicity,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_no_reward_or_related
)

User = get_user_model()


class Habit(models.Model):
    """Модель привычки."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True, null=True)
    place = models.CharField(_('Место'), max_length=255, blank=True, null=True)
    action = models.CharField(_('Действие'), max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")


    periodicity = models.PositiveIntegerField(
        _('Периодичность (в днях)'),
        validators=[validate_periodicity],
        default=1,
        help_text=_('Как часто нужно выполнять привычку (в днях)')
    )

    time_to_complete = models.TimeField(_('Время выполнения'))

    estimated_duration = models.PositiveIntegerField(
        _('Расчетное время выполнения (в секундах)'),
        validators=[validate_execution_time],
        default=60,
        help_text=_('Сколько времени предположительно займет выполнение')
    )

    is_pleasant = models.BooleanField(
        _('Приятная привычка'),
        default=False,
        help_text=_('Отметьте, если это приятная привычка')
    )

    is_public = models.BooleanField(
        _('Публичная привычка'),
        default=False,
        help_text=_('Отметьте, если привычка будет доступна всем пользователям')
    )

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_habits',
        verbose_name=_('Связанная привычка')
    )

    reward = models.CharField(
        _('Вознаграждение'),
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Привычка')
        verbose_name_plural = _('Привычки')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def clean(self):
        """Проверка бизнес-логики модели."""
        super().clean()

        # Проверка на одновременное наличие вознаграждения и связанной привычки
        if self.reward and self.related_habit:
            raise ValidationError(
                _('Нельзя одновременно указывать связанную привычку и вознаграждение.')
            )

        # Проверка что связанная привычка приятная
        if self.related_habit:
            validate_related_habit_is_pleasant(self, self.related_habit)

        # Проверка ограничений для приятных привычек
        validate_pleasant_habit_no_reward_or_related(self)

    def save(self, *args, **kwargs):
        # Удаляем вызов full_clean() для избежания ошибки 500
        super().save(*args, **kwargs)


class HabitCompletion(models.Model):
    """Модель для отслеживания выполнения привычек."""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habit_completions'
    )
    completed_at = models.DateTimeField(
        _('Время выполнения'),
        default=timezone.now
    )
    is_successful = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Выполнение привычки')
        verbose_name_plural = _('Выполнения привычек')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.habit.name} ({self.completed_at})"


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    chat_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.chat_id}"