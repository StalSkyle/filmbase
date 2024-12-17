# Generated by Django 5.1.3 on 2024-11-18 17:00

import datetime
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Страна',
                'verbose_name_plural': 'Страны',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=400, verbose_name='Имя')),
                ('origin_name', models.CharField(blank=True, max_length=400, null=True, verbose_name='Имя в оригинале')),
                ('birthday', models.DateField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(limit_value=datetime.date.today)], verbose_name='Дата рождения')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/', verbose_name='Фото')),
                ('kinopoisk_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Kinopoisk ID')),
            ],
            options={
                'verbose_name': 'Персона',
                'verbose_name_plural': 'Персоны',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024, verbose_name='Имя')),
                ('origin_name', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Название (в оригинале)')),
                ('slogan', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Девиз')),
                ('length', models.PositiveIntegerField(blank=True, null=True, verbose_name='Продолжительность')),
                ('year', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(limit_value=1885)], verbose_name='Год выпуска')),
                ('trailer_url', models.URLField(blank=True, null=True, verbose_name='Трейлер')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='covers/', verbose_name='Постер')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('kinopoisk_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Kinopoisk ID')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.country', verbose_name='Страна')),
                ('genres', models.ManyToManyField(to='films.genre', verbose_name='Жанр')),
                ('director', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directed_films', to='films.person', verbose_name='Режиссер')),
                ('people', models.ManyToManyField(to='films.person', verbose_name='Актеры')),
            ],
            options={
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
                'ordering': ['name'],
            },
        ),
    ]
