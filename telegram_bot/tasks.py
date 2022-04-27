import os
from time import sleep

import requests
from bs4 import BeautifulSoup, NavigableString
from celery import chain
from django.db import connection
from django.db.models import QuerySet

from django_telegrambot import settings
from django_telegrambot.celery import app
from telegram_bot.models import ActualCurrencyInfo, TelegramUser
from telegram_bot.utils import get_weather_message

from . import consts
from .instance import bot_instance

CITIES = {
    "1": ("minsk", "Минск"),
    "2": ("brest", "Брест"),
    "3": ("vitebsk", "Витебск"),
    "4": ("gomel", "Гомель"),
    "5": ("grodno", "Гродно"),
    "6": ("mogilev", "Могилев"),
}

SOURCE = "https://myfin.by/currency-old/"


@app.task
def updating_cache_files():
    os.mkdir(settings.CURRENCY_CACHE_PATH) if not os.path.exists(settings.CURRENCY_CACHE_PATH) else None
    cache_files = os.listdir(settings.CURRENCY_CACHE_PATH)
    if cache_files:
        map(
            lambda file_to_remove: os.remove(os.path.join(settings.CURRENCY_CACHE_PATH, file_to_remove)),
            os.listdir(settings.CURRENCY_CACHE_PATH),
        )

    for name in CITIES.values():
        url = SOURCE + name[0]
        file = os.path.join(settings.CURRENCY_CACHE_PATH, f"temporary_{name[0]}.html")
        response = requests.get(url, headers={"User-agent": "your bot 0.2"})
        print(f"Response status: {response.status_code}")
        if response.status_code == 429:
            app.control.revoke(updating_cache_files.request.id)
        with open(file, "w") as f:
            f.write(response.text)
        sleep(30)


@app.task
def parsing_data(*args):
    cities = list(map(lambda elem: elem[0], CITIES.values()))
    fields = [f.name for f in ActualCurrencyInfo._meta.fields][5:]
    objects = []
    for file in os.listdir(settings.CURRENCY_CACHE_PATH):
        with open(os.path.join(settings.CURRENCY_CACHE_PATH, file)) as f:
            html = f.read()
        try:
            city = list(filter(lambda elem: elem in file, cities))[0]
        except IndexError:
            city = "Unknown_city"
        soup = BeautifulSoup(html, "lxml")
        table_currency = soup.find("tbody", {"id": "currency_tbody"})
        banks = table_currency.findAll("tr")
        for bank in banks:
            data = {}
            if bank.has_attr("data-bank_id"):
                counter = 0
                for td in bank:
                    if not isinstance(td, NavigableString):
                        if td.find("span"):
                            bank_name = td.find("span").get_text()
                            data["city"] = city
                            data["bank"] = bank_name
                            continue
                        data[fields[counter]] = td.get_text() if td.get_text() != "-" else None
                        counter += 1
                objects.append(ActualCurrencyInfo(**data))

    ActualCurrencyInfo.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT setval('telegram_bot_actualcurrencyinfo_id_seq', 1);
                        UPDATE telegram_bot_actualcurrencyinfo SET id = DEFAULT;"""
        )
    ActualCurrencyInfo.objects.bulk_create(objects)
    return len(objects)


@app.task
def updating_and_parsing_data():
    chain_tasks = chain(updating_cache_files.s(), parsing_data.s())
    chain_tasks()


@app.task
def send_morning_weather():
    users_info: QuerySet = TelegramUser.objects.filter(settings__is_beat_weather=True).values_list(
        "telegram_id", "city_location"
    )
    for user_id, city in users_info:
        bot_instance.send_message(user_id, get_weather_message(city or consts.WeatherResponses.DEFAULT_CITY.value))
