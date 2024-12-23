from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Film, Person, Country, Genre, NotificationSettings, User
from django.conf import settings
from celery import shared_task
import datetime


# храним старые данные (надо ли)
old_instances = {}

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

# изменения в фильме

# а надо ли это ещё вообще
@receiver(pre_save, sender=Film)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        # храним старые данные
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)

# +- готово
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
            # print(user, user.notification_settings.user_mail)
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
            if not_settings.notification_period == 'daily': # следующий день 12:00
                schedule_time = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(12, 0))
            elif not_settings.notification_period == 'weekly': # следующий понедельник 12:00
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
            elif not_settings.notification_period == 'monthly': # первое число следующего месяца, 12:00
                current_date = datetime.datetime.now()
                if current_date.month == 12:
                    next_month = 1
                    next_year = current_date.year + 1
                else:
                    next_month = current_date.month + 1
                    next_year = current_date.year
                schedule_time = datetime.datetime(next_year, next_month,
                                                        1, 12, 0)

            print(user, user.notification_settings.user_mail, schedule_time)
            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление о фильме: {action}", message, schedule_time]
            )

# что тут вообще происходит
@receiver(post_delete, sender=Film)
def notify_on_delete(sender, instance, **kwargs):
    action = 'everything'  # Deletion is only covered under 'everything'
    message = f"Фильм '{instance.name}' был удален."

    # Get all users who have 'everything' notification type
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
            if not_settings.notification_period == 'daily':  # следующий день 12:00
                schedule_time = datetime.datetime.combine(
                    datetime.date.today() + datetime.timedelta(days=1),
                    datetime.time(12, 0))
            elif not_settings.notification_period == 'weekly':  # следующий понедельник 12:00
                now = datetime.datetime.now()
                if now.weekday() == 0 and now.hour < 12:
                    next_monday = now.replace(hour=12, minute=0, second=0,
                                              microsecond=0)
                else:
                    days_ahead = (7 - now.weekday()) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    next_monday = now + datetime.timedelta(days=days_ahead)
                    schedule_time = next_monday.replace(hour=12, minute=0,
                                                        second=0,
                                                        microsecond=0)
            elif not_settings.notification_period == 'monthly':  # первое число следующего месяца, 12:00
                current_date = datetime.datetime.now()
                if current_date.month == 12:
                    next_month = 1
                    next_year = current_date.year + 1
                else:
                    next_month = current_date.month + 1
                    next_year = current_date.year
                schedule_time = datetime.datetime(next_year, next_month,
                                                  1, 12, 0)

            # запланировать отправку
            schedule_notification_email.apply_async(
                args=[user.email, f"Уведомление о фильме: {action}", message],
                eta=schedule_time
            )


# изменения у актёра
@receiver(pre_save, sender=Person)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)


@receiver(post_save, sender=Person)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Добавлен новый актёр: {instance.name}")
    else:
        old_instance = old_instances.get(instance.pk)
        if old_instance:
            changes = {}
            for field in sender._meta.fields:
                old_value = getattr(old_instance, field.name)
                new_value = getattr(instance, field.name)
                if old_value != new_value:
                    changes[field.name] = {'old': old_value, 'new': new_value}
            if changes:
                print("Изменены данные актёра")
                for field in changes:
                    if field != 'updated_at':
                        print(
                            f"Было: {changes[field]['old']}, стало: {changes[field]['new']}")

    # удаляем старые данные
    old_instances.pop(instance.pk, None)


@receiver(post_delete, sender=Person)
def print_on_delete(sender, instance, **kwargs):
    print(f"Удалили актёра {instance.name}")


# добавление/удаление жанра
@receiver(post_save, sender=Genre)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Добавлен новый жанр фильмов: {instance.name}")


@receiver(post_delete, sender=Genre)
def print_on_delete(sender, instance, **kwargs):
    print(f"Удалён жанр {instance.name}")


# добавление/удаление страны
@receiver(post_save, sender=Country)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Теперь можно посмотреть фильмы из страны {instance.name}")


@receiver(post_delete, sender=Country)
def print_on_delete(sender, instance, **kwargs):
    print(f"Больше нет фильмов из страны {instance.name}")
