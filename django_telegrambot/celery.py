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

app.conf.timezone = "Europe/Minsk"
app.conf.update(BROKER_URL=settings.BROKER_URL)

# app.conf.beat_schedule = {
#     ,
# }

app.conf.beat_schedule = {
    "morning_weather": {"task": "telegram_bot.tasks.send_morning_weather", "schedule": crontab(hour=7, minute=15)},
    "upload_currencies": {
        "task": "telegram_bot.tasks.updating_and_parsing_data",
        "schedule": crontab(minute=0, hour="*/2"),
    },
}
app.autodiscover_tasks(settings.INSTALLED_APPS)

if __name__ == "__main__":
    app.start()
