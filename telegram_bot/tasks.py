import os
from time import sleep

import requests
from bs4 import BeautifulSoup, NavigableString
from celery import chain

from django_telegrambot import settings
from django_telegrambot.celery import app

CITIES = {
    "1": ("minsk", "Минск"),
    "2": ("brest", "Брест"),
    "3": ("vitebsk", "Витебск"),
    "4": ("gomel", "Гомель"),
    "5": ("grodno", "Гродно"),
    "6": ("mogilev", "Могилев"),
}
PROPOSAL = (
    ("usd_buy", "best_usd_buy"),
    ("usd_sell", "best_usd_sell"),
    ("euro_buy", "best_euro_buy"),
    ("euro_sell", "best_euro_sell"),
    ("rub_buy", "best_rub_buy"),
    ("rub_sell", "best_rub_sell"),
    ("usd_buy_from euro", "best_usd_buy_from euro"),
    ("usd_sell_from euro", "best_usd_sell_from euro"),
)
SOURCE = "https://myfin.by/currency/"


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
        response = requests.get(url, headers={"User-agent": "your bot 0.1"})
        print(f"Response status: {response.status_code}")
        with open(file, "w") as f:
            f.write(response.text)
        sleep(1)


@app.task
def parsing_data(*args):
    dict_currency = {}
    dict_best_currency = {}
    for file in os.listdir(settings.CURRENCY_CACHE_PATH):
        with open(os.path.join(settings.CURRENCY_CACHE_PATH, file)) as f:
            html = f.read()
        soup = BeautifulSoup(html, "lxml")
        table_currency = soup.find("tbody", {"id": "currency_tbody"})
        banks = table_currency.findAll("tr")
        bank_name = ""
        for bank in banks:
            if bank.has_attr("data-bank_id"):
                counter = 0
                for td in bank:
                    if not isinstance(td, NavigableString):
                        if td.find("span"):
                            bank_name = td.find("span").get_text()
                            dict_currency[bank_name] = {}
                            dict_best_currency[bank_name] = {}
                            continue
                        if not dict_currency[bank_name].get(PROPOSAL[counter][0]):
                            dict_currency[bank_name].update({PROPOSAL[counter][0]: td.get_text()})
                            if td.has_attr("class") and td.attrs["class"][0] == "best":
                                dict_best_currency[bank_name].update({PROPOSAL[counter][1]: td.get_text()})
                            counter += 1
                            continue
    dict_best_currency = {bank: currencies for bank, currencies in dict_best_currency.items() if currencies}
    return [dict_currency, dict_best_currency]


@app.task
def updating_and_parsing_data():
    chain_tasks = chain(updating_cache_files.s(), parsing_data.s())
    chain_tasks()
