from celery import shared_task
from django.core.mail import send_mail
from .models import User, NotificationSettings

import logging

logger = logging.getLogger(__name__)

@shared_task
def print_test_message():
    logger.info("test")
    print("test")

# ежедневная заданча (периодические задачи запускаются из celery.py)
@shared_task
def send_daily_changes():
    users = User.objects.filter(notification_settings__notification_period='daily')
    for user in users:
        not_settings = user.notification_settings
        if not_settings.daily_changes:
            send_mail(
                'Изменения за день',
                not_settings.daily_changes,
                's1rodion123@gmail.com',
                [not_settings.user_mail],
                fail_silently=True,
            )
            # очистить ежедневные изменения после отправки
            not_settings.daily_changes = ''
            not_settings.save()

# еженедельное задание
@shared_task
def send_weekly_changes():
    users = User.objects.filter(notification_settings__notification_period='weekly')
    for user in users:
        not_settings = user.notification_settings
        if not_settings.weekly_changes:
            send_mail(
                'Изменения за неделю',
                not_settings.weekly_changes,
                's1rodion123@gmail.com',
                [not_settings.user_mail],
                fail_silently=True,
            )
            not_settings.weekly_changes = ''
            not_settings.save()

# ежемесячное задание
@shared_task
def send_monthly_changes():
    users = User.objects.filter(notification_settings__notification_period='monthly')
    for user in users:
        not_settings = user.notification_settings
        if not_settings.monthly_changes:
            send_mail(
                'Изменения за месяц',
                not_settings.monthly_changes,
                's1rodion123@gmail.com',
                [not_settings.user_mail],
                fail_silently=True,
            )
            not_settings.monthly_changes = ''
            not_settings.save()