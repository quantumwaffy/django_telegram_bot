import asyncio

from django.db import connection
from django.db.models import QuerySet
from telegram import error as tg_errors

from django_telegrambot.celery import app
from telegram_bot.models import ActualCurrencyInfo, TelegramUser
from telegram_bot.utils import get_weather_message

from . import consts, currency_parser
from .instance import bot_instance


@app.task
def update_currency_data() -> int:
    currency_objects: list[ActualCurrencyInfo] = asyncio.run(currency_parser.get_currency_rate())
    ActualCurrencyInfo.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT setval('telegram_bot_actualcurrencyinfo_id_seq', 1);
                        UPDATE telegram_bot_actualcurrencyinfo SET id = DEFAULT;"""
        )
    ActualCurrencyInfo.objects.bulk_create(currency_objects)
    return len(currency_objects)


@app.task
def send_morning_weather():
    users_info: QuerySet = TelegramUser.objects.filter(settings__beat_weather__isnull=False).values_list(
        "telegram_id", "city_location"
    )
    for user_id, city in users_info:
        try:
            bot_instance.send_message(user_id, get_weather_message(city or consts.WeatherResponses.DEFAULT_CITY.value))
        except tg_errors.Unauthorized:
            continue
