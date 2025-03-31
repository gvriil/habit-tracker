from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Расширенная модель пользователя."""

    # Дополнительные поля для Telegram
    telegram_id = models.CharField(_('ID в Telegram'), max_length=50, blank=True, null=True)
    telegram_username = models.CharField(_('Username в Telegram'), max_length=100, blank=True,
                                         null=True)

    # Настройки уведомлений
    notify_before_minutes = models.PositiveIntegerField(
        _('Напоминать за (минут)'),
        default=30,
        help_text=_('За сколько минут присылать уведомления о привычке')
    )
    telegram_notifications = models.BooleanField(_('Уведомления в Telegram'), default=False)

    # Статистика
    streak_days = models.PositiveIntegerField(_('Текущая серия дней'), default=0)
    longest_streak = models.PositiveIntegerField(_('Самая длинная серия дней'), default=0)

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.username