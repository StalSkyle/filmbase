from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import NotificationSettings

@receiver(post_save, sender=NotificationSettings)
def on_save(sender, **kwargs):
    print("Данные изменены")

@receiver(post_delete, sender=NotificationSettings)
def on_delete(sender, **kwargs):
    print("Данные изменены")