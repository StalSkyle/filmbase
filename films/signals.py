from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Film, Person, Country, Genre, NotificationSettings, User
from django.conf import settings
from celery import shared_task
import datetime


DAILY_CHANGES = []
WEEKLY_CHANGES = []
MONTHLY_CHANGES = []

# запланировать отправку сообщения
@shared_task
def schedule_notification_email(user_email, subject, message, schedule_time):
    if datetime.datetime.now() >= schedule_time:
        send_mail(
            subject,
            message,
            's1rodion123@gmail.com',
            [user_email],
            fail_silently=True,
        )
    else:
        # если время ещё не настало
        schedule_notification_email.apply_async(
            args=[user_email, subject, message, schedule_time]
        )

# получить дату отправки письма
def get_schedule_time(period):
    schedule_time = '' #?
    if period == 'daily':  # следующий день 12:00
        schedule_time = datetime.datetime.combine(
            datetime.date.today() + datetime.timedelta(days=1),
            datetime.time(12, 0))
    elif period == 'weekly':  # следующий понедельник 12:00
        now = datetime.datetime.now()
        if now.weekday() == 0 and now.hour < 12:
            schedule_time = now.replace(hour=12, minute=0, second=0,
                                        microsecond=0)
        else:
            days_ahead = (7 - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_monday = now + datetime.timedelta(days=days_ahead)
            schedule_time = next_monday.replace(hour=12, minute=0,
                                                second=0, microsecond=0)
    elif period.notification_period == 'monthly':  # первое число следующего месяца, 12:00
        current_date = datetime.datetime.now()
        if current_date.month == 12:
            next_month = 1
            next_year = current_date.year + 1
        else:
            next_month = current_date.month + 1
            next_year = current_date.year
        schedule_time = datetime.datetime(next_year, next_month,
                                          1, 12, 0)
    return schedule_time

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ О ФИЛЬМЕ

# при сохранении фильма
@receiver(post_save, sender=Film)
def notify_on_save(sender, instance, created, **kwargs):
    if created:
        action = 'add'
        message = f"Новый фильм добавлен: {instance.name}"
    else:
        action = 'add_change'
        message = f"Фильм '{instance.name}' был изменен."

    # выбираем пользователей с необходимой отметкой
    users = User.objects.filter(
        notification_settings__notification_types__in=[action, 'everything']
    )

    for user in users:
        not_settings = user.notification_settings # notification settings
        if not_settings.notification_period == 'instant':
            try:
                send_mail(
                    action,
                    message,
                    's1rodion123@gmail.com',
                    [user.notification_settings.user_mail],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка при отправке email пользователю {user}: {e}")
        else:
            schedule_time = get_schedule_time(not_settings.notification_period)
            print(user, user.notification_settings.user_mail, schedule_time)

            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление о фильме: {action}", message, schedule_time]
            )

# при удалении
@receiver(post_delete, sender=Film)
def notify_on_delete(sender, instance, **kwargs):
    action = 'everything'
    message = f"Фильм '{instance.name}' был удален."

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        not_settings = user.notification_settings
        if settings.notification_period == 'instant':
            try:
                send_mail(
                    action,
                    message,
                    's1rodion123@gmail.com',
                    [user.notification_settings.user_mail],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка при отправке email пользователю {user}: {e}")
        else:
            schedule_time = get_schedule_time(not_settings.notification_period)
            print(user, user.notification_settings.user_mail, schedule_time)

            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление о фильме: {action}", message, schedule_time]
            )

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ ОБ АКТЁРЕ

# при сохранении
@receiver(post_save, sender=Person)
def notify_on_save(sender, instance, created, **kwargs):
    if created:
        action = 'everything'
        message = f"Новый актёр добавлен: {instance.name}"
    else:
        action = 'everything'
        message = f"Информация об актёре '{instance.name}' была изменена."
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )
    for user in users:
        not_settings = user.notification_settings
        if settings.notification_period == 'instant':
            try:
                send_mail(
                    action,
                    message,
                    's1rodion123@gmail.com',
                    [user.notification_settings.user_mail],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка при отправке email пользователю {user}: {e}")
        else:
            schedule_time = get_schedule_time(not_settings.notification_period)
            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление о фильме: {action}", message, schedule_time]
            )

# при удалении актёра
@receiver(post_delete, sender=Person)
def notify_on_delete(sender, instance, **kwargs):
    action = 'everything'
    message = f"Актёр '{instance.name}' был удален."

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        not_settings = user.notification_settings
        if settings.notification_period == 'instant':
            try:
                send_mail(
                    action,
                    message,
                    's1rodion123@gmail.com',
                    [user.notification_settings.user_mail],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка при отправке email пользователю {user}: {e}")
        else:
            schedule_time = get_schedule_time(not_settings.notification_period)
            print(user, user.notification_settings.user_mail, schedule_time)

            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление об актёре: {action}", message,
                      schedule_time]
            )

# добавление/удаление жанра
@receiver(post_save, sender=Genre)
def notify_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Добавлен новый жанр фильмов: {instance.name}")


@receiver(post_delete, sender=Genre)
def notify_on_delete(sender, instance, **kwargs):
    print(f"Удалён жанр {instance.name}")


# добавление/удаление страны
@receiver(post_save, sender=Country)
def notify_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Теперь можно посмотреть фильмы из страны {instance.name}")


@receiver(post_delete, sender=Country)
def notify_on_delete(sender, instance, **kwargs):
    print(f"Больше нет фильмов из страны {instance.name}")
