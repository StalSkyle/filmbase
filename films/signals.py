from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import NotificationSettings, Film

# Dictionary to store old instances
old_instances = {}

@receiver(pre_save, sender=NotificationSettings)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        # Store the old instance before it's updated
        old_instances[instance.pk] = sender.objects.get(pk=instance.pk)

@receiver(post_save, sender=NotificationSettings)
def print_on_save(sender, instance, created, **kwargs):
    if created:
        print("Создана новая запись.")
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
                print(f"Данные изменены: {changes}")
            else:
                print("Данные не изменились.")
        else:
            print("Данные не изменились.")
    # Remove the old instance data to free up memory
    old_instances.pop(instance.pk, None)