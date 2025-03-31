from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TelegramState(models.Model):
    """Модель для хранения состояния диалога с пользователем в Telegram."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_states',
        verbose_name=_('Пользователь')
    )
    telegram_id = models.CharField(_('ID в Telegram'), max_length=50)
    state = models.CharField(_('Состояние диалога'), max_length=100, default='start')
    context = models.JSONField(_('Контекст диалога'), default=dict, blank=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Состояние в Telegram')
        verbose_name_plural = _('Состояния в Telegram')

    def __str__(self):
        return f"{self.user.username} - {self.state}"


class NotificationLog(models.Model):
    """Модель для логирования отправленных уведомлений."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs',
        verbose_name=_('Пользователь')
    )
    habit = models.ForeignKey(
        'habits.Habit',
        on_delete=models.CASCADE,
        related_name='notification_logs',
        verbose_name=_('Привычка')
    )
    sent_at = models.DateTimeField(_('Время отправки'), auto_now_add=True)
    message = models.TextField(_('Текст сообщения'))
    is_delivered = models.BooleanField(_('Доставлено'), default=False)

    class Meta:
        verbose_name = _('Лог уведомлений')
        verbose_name_plural = _('Логи уведомлений')
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.user.username} - {self.habit.name} - {self.sent_at.strftime('%d.%m.%Y %H:%M')}"