from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Film, Person, Country, Genre, NotificationSettings, User

from celery import shared_task

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


# отправить уведомления или изменить поля у пользователей
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
        # добавить сообщение к нужному полю
        if period == 'daily':
            not_settings.daily_changes += message + '\n\n'
        elif period == 'weekly':
            not_settings.weekly_changes += message + '\n\n'
        elif period == 'monthly':
            not_settings.monthly_changes += message + '\n\n'
        not_settings.save()


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
