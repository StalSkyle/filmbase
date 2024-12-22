from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Film, Person

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
        print("Создан новый фильм.")
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
                        print(f"Было: {changes[field]['old']}, стало: {changes[field]['new']}")
    # удаляем старые данные
    old_instances.pop(instance.pk, None)

@receiver(post_delete, sender=Film)
def print_on_delete(sender, **kwargs):
    print("Удалили фильм")

# изменения у актёра
@receiver(pre_save, sender=Person)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)

@receiver(post_save, sender=Person)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print("Добавили актёра")
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
                        print(f"Было: {changes[field]['old']}, стало: {changes[field]['new']}")

    # удаляем старые данные
    old_instances.pop(instance.pk, None)

@receiver(post_delete, sender=Person)
def print_on_delete(sender, instance, **kwargs):
    for field in instance._meta.fields:
        field_name = field.name
        if field_name == 'name':
            field_value = getattr(instance, field_name)
            print(f"Удалили актёра, {field_value}")
