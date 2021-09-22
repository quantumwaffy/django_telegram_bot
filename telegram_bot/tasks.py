import os
from time import sleep

import requests
from bs4 import BeautifulSoup

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
SOURCE = "https://myfin.by/currency/"


@app.task
def update_cache_files():

    cache_path = os.path.join(os.path.join(settings.BASE_DIR), "CACHE_CURRENCY")
    os.mkdir(cache_path) if not os.path.exists(cache_path) else None
    cache_files = os.listdir(cache_path)
    if cache_files:
        map(lambda file_to_remove: os.remove(os.path.join(cache_path, file_to_remove)), os.listdir(cache_path))

    for name in CITIES.values():
        url = SOURCE + name[0]
        file = os.path.join(cache_path, f"temporary_{name[0]}.html")
        response = requests.get(url, headers={"User-agent": "your bot 0.1"})
        print(response.status_code)
        with open(file, "w") as f:
            f.write(str(BeautifulSoup(response.text, "lxml")))
        sleep(1)
