from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import Film, Person, Country, Genre

# храним старые данные
old_instances = {}


# изменения в фильме
@receiver(pre_save, sender=Film)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        # храним старые данные
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)


@receiver(post_save, sender=Film)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print(f"Добавлен новый фильм: {instance.name}")
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
                print(f"Изменены данные фильма")
                for field in changes:
                    if field != 'updated_at':
                        print(
                            f"Было: {changes[field]['old']}, стало: {changes[field]['new']}")
    # удаляем старые данные
    old_instances.pop(instance.pk, None)


@receiver(post_delete, sender=Film)
def print_on_delete(sender, instance, **kwargs):
    print(f"Удалён фильм {instance.name}")


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
