from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duration(value):
    """Проверяет, что продолжительность не превышает 120 минут"""
    if value > 120:
        raise ValidationError(
            _('Продолжительность привычки не может превышать 120 минут'),
        )


def validate_related_habit(related_habit, reward):
    """
    Проверяет, что связанная привычка является приятной
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            _('Связанная привычка должна быть приятной'),
        )


def validate_reward(reward, related_habit):
    """
    Проверяет, что одновременно не указаны и награда, и связанная привычка
    """
    if reward and related_habit:
        raise ValidationError(
            _('Нельзя одновременно указывать связанную привычку и вознаграждение'),
        )

def validate_not_both_reward_and_related(value):
    """
    Проверяет, что у привычки не заданы одновременно связанная привычка и вознаграждение.
    """
    related_habit = value.get('related_habit')
    reward = value.get('reward')

    if related_habit and reward:
        raise ValidationError(
            _('Нельзя одновременно указывать связанную привычку и вознаграждение.')
        )


def validate_execution_time(seconds):
    """
    Проверяет, что время выполнения привычки не превышает 120 секунд.
    """
    if seconds > 120:
        raise ValidationError(
            _('Время выполнения привычки не может превышать 120 секунд.')
        )


def validate_related_habit_is_pleasant(habit, related_habit):
    """
    Проверяет, что связанная привычка является приятной.
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            _('В связанные привычки можно указывать только приятные привычки.')
        )


def validate_pleasant_habit_no_reward_or_related(habit):
    """
    Проверяет, что у приятной привычки нет вознаграждения или связанной привычки.
    """
    if habit.is_pleasant and (habit.reward or habit.related_habit):
        raise ValidationError(
            _('У приятной привычки не может быть вознаграждения или связанной привычки.')
        )


def validate_periodicity(days):
    """
    Проверяет, что периодичность привычки не превышает 7 дней.
    """
    if days > 7:
        raise ValidationError(
            _('Привычку нельзя выполнять реже, чем раз в 7 дней.')
        )