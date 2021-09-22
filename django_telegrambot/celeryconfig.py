from kombu import Exchange, Queue

from . import settings

broker_url = settings.CELERY_BROKER

task_default_queue = "django_telegrambot"

task_queues = (Queue("django_telegrambot", Exchange("django_telegrambot"), routing_key="django_telegrambot"),)

imports = "telegram_bot.tasks"

try:
    from .local_settings_celery import *  # noqa
except ImportError:
    pass
