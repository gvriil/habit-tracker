from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TelegramState(models.Model):
    """Модель для хранения состояния диалога пользователя с ботом."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="telegram_states",
    )
    telegram_id = models.BigIntegerField(_("Telegram ID"), unique=True)
    state = models.CharField(_("Состояние диалога"), max_length=100, default="start")
    context = models.JSONField(_("Контекст диалога"), default=dict, blank=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Состояние Telegram")
        verbose_name_plural = _("Состояния Telegram")

    def __str__(self):
        return f"{self.user.username} ({self.state})"


class NotificationLog(models.Model):
    """Модель для логирования отправленных уведомлений."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="notification_logs",
    )
    habit = models.ForeignKey(
        "habits.Habit",
        verbose_name=_("Привычка"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sent_at = models.DateTimeField(_("Время отправки"), auto_now_add=True)
    message = models.TextField(_("Текст сообщения"))
    is_delivered = models.BooleanField(_("Доставлено"), default=False)

    # Новые поля для трекинга взаимодействия
    user_response = models.CharField(
        _("Ответ пользователя"), max_length=50, blank=True, null=True
    )
    response_time = models.DateTimeField(_("Время ответа"), blank=True, null=True)

    class Meta:
        verbose_name = _("Лог уведомлений")
        verbose_name_plural = _("Логи уведомлений")

    def __str__(self):
        habit_name = self.habit.name if self.habit else "Системное"
        return f"{self.user.username} - {habit_name} - {self.sent_at.strftime('%d.%m.%Y %H:%M')}"


class Achievement(models.Model):
    """Модель для хранения достижений пользователей."""

    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"))
    image = models.CharField(
        _("Эмодзи/Иконка"), max_length=50
    )  # Эмодзи для отображения в Telegram
    condition_type = models.CharField(_("Тип условия"), max_length=50)
    condition_value = models.IntegerField(_("Значение условия"))

    class Meta:
        verbose_name = _("Достижение")
        verbose_name_plural = _("Достижения")

    def __str__(self):
        return f"{self.name} ({self.image})"


class UserAchievement(models.Model):
    """Связь пользователей с полученными достижениями."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    achievement = models.ForeignKey(
        Achievement, verbose_name=_("Достижение"), on_delete=models.CASCADE
    )
    date_earned = models.DateTimeField(_("Дата получения"), auto_now_add=True)

    class Meta:
        verbose_name = _("Достижение пользователя")
        verbose_name_plural = _("Достижения пользователей")
        unique_together = ("user", "achievement")

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
