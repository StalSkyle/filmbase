# Generated by Django 5.1.4 on 2024-12-18 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0003_notificationsettings_user_mail'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notificationsettings',
            options={'verbose_name': 'Notification Setting', 'verbose_name_plural': 'Notification Settings'},
        ),
    ]