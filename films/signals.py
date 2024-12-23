from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Film, Person, Country, Genre, NotificationSettings, User
from django.conf import settings
from celery import shared_task
import datetime

# отправить уведомление определенному пользователю
@shared_task
def schedule_notification_email(user_email, subject, message):
    send_mail(
        subject,
        message,
        's1rodion123@gmail.com',
        [user_email],
        fail_silently=True,
    )
    # получить пользователя и его настройки уведомлений
    user = User.objects.get(notification_settings__user_mail=user_email)
    period = user.notification_settings.notification_period
    if period != 'instant': # передвинуть дату вперед
        reschedule_notification.apply_async(
            args=[user.id, period, subject, message],
            eta=get_schedule_time(period)
        )

# передвинуть дату, когда в следующий раз уведомить
@shared_task
def reschedule_notification(user_id, period, subject, message):
    user = User.objects.get(id=user_id)
    schedule_time = get_schedule_time(period)
    schedule_notification_email.apply_async(
        args=[user.notification_settings.user_mail, subject, message],
        eta=schedule_time
    )

# получить дату отправки письма
def get_schedule_time(period):
    now = datetime.datetime.now()
    if period == 'daily':
        # следующий день в 12:00
        next_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if next_time < now:
            next_time += datetime.timedelta(days=1)
        return next_time
    elif period == 'weekly':
        # следующий понедельник в 12:00
        days_ahead = (7 - now.weekday()) % 7
        next_time = now + datetime.timedelta(days=days_ahead)
        next_time = next_time.replace(hour=12, minute=0, second=0, microsecond=0)
        if next_time < now:
            next_time += datetime.timedelta(days=7)
        return next_time
    elif period == 'monthly':
        # первый день следующего месяца, 12:00
        if now.day == 1 and now.hour < 12:
            year = now.year
            month = now.month
        else:
            if now.month == 12:
                year = now.year + 1
                month = 1
            else:
                year = now.year
                month = now.month + 1
        next_time = datetime.datetime(year, month, 1, 12, 0)
        if next_time < now:
            if month == 1:
                year += 1
            else:
                month += 1
            next_time = datetime.datetime(year, month, 1, 12, 0)
        return next_time
    else:
        return now

# отправить или запланировать уведомление
def send_notification(user, action, message):
    not_settings = user.notification_settings
    period = not_settings.notification_period
    if period == 'instant':
        try:
            send_mail(
                action,
                message,
                's1rodion123@gmail.com',
                [not_settings.user_mail],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Ошибка при отправке email пользователю {user}: {e}")
    else:
        schedule_time = get_schedule_time(period)
        # планируем уведомление
        # print('ЗАПЛАНИРОВАЛИ УВЕДОМЛЕНИЕ')
        # print(not_settings.user_mail)
        # print(schedule_time)
        schedule_notification_email.apply_async(
            args=[not_settings.user_mail, action, message],
            eta=schedule_time
        )


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
        send_notification(user, action, message)

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
        send_notification(user, action, message)

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ ОБ АКТЁРЕ

# при сохранении
@receiver(post_save, sender=Person)
def notify_on_save(sender, instance, created, **kwargs):
    action = 'everything'
    message = f"Актёр {instance.name} был изменён."

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        send_notification(user, action, message)

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
        send_notification(user, action, message)

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ О ЖАНРЕ

# добавление
@receiver(post_save, sender=Genre)
def notify_on_save(sender, instance, created, **kwargs):
    action = 'everything'
    message = f"Добавлен новый жанр фильмов: {instance.name}"

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        send_notification(user, action, message)

# удаление
@receiver(post_delete, sender=Genre)
def notify_on_delete(sender, instance, **kwargs):
    action = 'everything'
    message = f"Жанр фильмов '{instance.name}' был удален."

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        send_notification(user, action, message)

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ О СТРАНЕ

# добавление
@receiver(post_save, sender=Country)
def notify_on_save(sender, instance, created, **kwargs):
    action = 'everything'
    message = f"Теперь можно посмотреть фильмы из страны {instance.name}"

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        send_notification(user, action, message)

# удаление
@receiver(post_delete, sender=Country)
def notify_on_delete(sender, instance, **kwargs):
    action = 'everything'
    message = f"Больше нет фильмов из страны {instance.name}."

    # получить пользователей, которые подписаны на все уведомления
    users = User.objects.filter(
        notification_settings__notification_types='everything'
    )

    for user in users:
        send_notification(user, action, message)
