from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmbase.settings')

app = Celery('filmbase')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.update(
    timezone='UTC',
)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-daily-changes': {
        'task': 'films.tasks.send_daily_changes',
        # 'schedule': crontab(hour='12', minute='0'),
        'schedule': crontab(minute='*/1'),
    },
    'send-weekly-changes': {
        'task': 'films.tasks.send_weekly_changes',
        'schedule': crontab(hour='12', minute='0', day_of_week='monday'),
    },
    'send-monthly-changes': {
        'task': 'films.tasks.send_monthly_changes',
        'schedule': crontab(hour='12', minute='0', day_of_month='1'),
    },
    'print-test-message-every-minute': {
        'task': 'films.tasks.print_test_message',
        'schedule': crontab(minute='*'),  # Выполняется каждую минуту
    },
}
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')