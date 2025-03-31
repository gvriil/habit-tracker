import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('habits_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-habits-every-10-minutes': {
        'task': 'habits.tasks.send_habit_reminders',
        'schedule': crontab(minute='*/10'),
    },
    'daily-statistics': {
        'task': 'habits.tasks.send_daily_statistics',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9 утра
    },
    'weekly-schedule': {
        'task': 'habits.tasks.schedule_weekly_reminders',
        'schedule': crontab(day_of_week='mon', hour=0, minute=0),  # Каждый понедельник
    },
}