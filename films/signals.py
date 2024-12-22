from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Film, Person, Country, Genre, NotificationSettings, User

# храним старые данные
old_instances = {}

# изменения в фильме
@receiver(pre_save, sender=Film)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        # храним старые данные
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)

@receiver(post_save, sender=Film)
def notify_on_save(sender, instance, created, **kwargs):
    if created:
        action = 'add'
        message = f"Новый фильм добавлен: {instance.name}"
    else:
        action = 'add_change'
        message = f"Фильм '{instance.name}' был изменен."

    # Get all users with relevant notification settings
    users = User.objects.filter(
        notification_settings__notification_types__in=[action, 'everything']
    )

    for user in users:
        settings = user.notification_settings
        if settings.notification_period == 'instant':
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


@receiver(post_delete, sender=Film)
def notify_on_delete(sender, instance, **kwargs):
    # Get all users with 'instant' notifications and appropriate types
    users_to_notify = NotificationSettings.objects.filter(
        notification_period='instant',
        notification_types__in=['add_change', 'everything']
    ).select_related('user')

    for setting in users_to_notify:
        user = setting.user
        user_email = setting.user_email if setting.user_email else user.email
        if not user_email:
            continue  # Skip if no email is provided

        subject = 'Фильм удален'
        message = f"Удалён фильм {instance.name}"

        send_mail(
            subject=subject,
            message=message,
            from_email='s1rodion123@gmail.com',
            recipient_list=[user_email],
            fail_silently=False,
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
