import os

from celery import Celery
from celery.schedules import crontab

from django_telegrambot import celeryconfig, settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_telegrambot.settings")

app = Celery("django_telegrambot")

app.config_from_object(celeryconfig)

app.conf.task_routes = {
    "telegram_bot.tasks.*": {"queue": "django_telegrambot", "routing_key": "django_telegrambot"},
}

app.conf.enable_utc = False

app.conf.beat_schedule = {
    "upload_currencies": {"task": "telegram_bot.tasks.updating_and_parsing_data", "schedule": crontab(minute="*/15")},
}
app.autodiscover_tasks(settings.INSTALLED_APPS)

if __name__ == "__main__":
    app.start()
