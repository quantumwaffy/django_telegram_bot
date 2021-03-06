from kombu import Exchange, Queue

from . import settings

broker_url = settings.BROKER_URL

task_default_queue = "django_telegrambot"

task_queues = (Queue("django_telegrambot", Exchange("django_telegrambot"), routing_key="django_telegrambot"),)

imports = "telegram_bot.tasks"
