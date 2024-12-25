# Система уведомлений Filmbase

## Описание проекта

Этот проект представляет собой модификацию оригинального [проекта Filmbase2024](https://github.com/aialeksandrov/filmbase2024). В него добавлена система отправки уведомлений пользователям о произошедших изменениях в базе данных. Пользователи могут подписываться на уведомления, настраивать предпочтения по частоте и типам уведомлений, а также получать обновления на свою электронную почту.

### Основные возможности
- **Настройка уведомлений**:
  - Частота уведомлений: мгновенно, раз в день, раз в неделю или раз в месяц.
  - Типы уведомлений:
    - Добавление нового фильма.
    - Добавление нового фильма или изменения существующих фильмов.
    - Все изменения для всех моделей.
- **Уведомления по электронной почте**: Реализована отправка как мгновенных, так и периодических уведомлений с использованием библиотеки `celery` и брокера сообщений `redis`.
- **Индивидуальные настройки**: Для каждого пользователя хранятся настройки уведомлений с использованием модели `NotificationSettings`.

---

## Детали реализации

### Модели

Для хранения предпочтений пользователей добавлена модель `NotificationSettings`:

```python
class NotificationSettings(MyModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('add', 'Добавление нового фильма'),
        ('add_change', 'Добавление нового фильма или изменение имеющегося'),
        ('everything', 'Все изменения'),
    ]

    PERIOD_CHOICES = [
        ('instant', 'Как только произошли изменения'),
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    ]

    user_mail = models.CharField("Почта пользователя", max_length=1024, blank=True, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    notification_types = models.CharField(max_length=20)
    notification_period = models.CharField(max_length=20)
    daily_changes = models.TextField(blank=True, null=True)
    weekly_changes = models.TextField(blank=True, null=True)
    monthly_changes = models.TextField(blank=True, null=True)
```

### Уведомления на основе сигналов

Для отслеживания изменений в моделях (`Film`, `Person`, `Country`, `Genre`) используются сигналы Django:

- **Сохранение**: Уведомления о добавлении новых записей или изменении существующих.
- **Удаление**: Уведомления об удалении записей.

### Задачи

Периодические задачи отправляют уведомления пользователям с настройками на ежедневные, еженедельные или ежемесячные уведомления. Задачи реализованы через Celery.

Пример задачи для отправки ежедневных уведомлений:

```python
@shared_task
def send_daily_changes():
    users = User.objects.filter(
        notification_settings__notification_period='daily')
    for user in users:
        not_settings = user.notification_settings
        if not_settings.daily_changes:
            send_mail(
                'Изменения за день',
                not_settings.daily_changes,
                'from@example.com',
                [not_settings.user_mail],
                fail_silently=True,
            )
            not_settings.daily_changes = ''
            not_settings.save()
```

---

## Зависимости

- **Celery**: Для управления асинхронными задачами.
- **Redis**: В качестве брокера сообщений для Celery.
- **Django Signals**: Для триггеров уведомлений при изменении данных.
- **Django Mail**: Для отправки email-уведомлений.

---

## Установка и настройка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/filmbase2024-notifications.git
   cd filmbase2024-notifications
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте и запустите Redis:
   ```bash
   redis-server
   ```

4. Запустите Celery:
   ```bash
   celery -A filmbase worker --loglevel=info
   celery -A filmbase beat --loglevel=info
   ```

5. Примените миграции:
   ```bash
   python manage.py migrate
   ```

6. Запустите сервер разработки Django:
   ```bash
   python manage.py runserver
   ```

---

## Использование

1. Зарегистрируйте нового пользователя и настройте параметры уведомлений через административную панель или пользовательский интерфейс.
2. Выполняйте операции (добавление, изменение, удаление) с моделями `Film`, `Person`, `Country` или `Genre`, чтобы увидеть работу уведомлений.
3. Уведомления будут отправлены на электронную почту в соответствии с пользовательскими настройками.

