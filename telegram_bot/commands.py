import os

from pyowm.commons.exceptions import APIResponseError
from telegram import Update
from telegram.ext import CallbackContext

from django_telegrambot.settings import STATICFILES_DIRS

from .instance import bot_instance, owm_instance
from .utils import return_bot_message


@return_bot_message
def command_start(update: Update, context: CallbackContext):
    user = update.effective_user
    with open(os.path.join(STATICFILES_DIRS[0], "images", "AnimatedSticker.tgs"), "rb") as f:
        bot_instance.send_sticker(update.effective_message.chat_id, f)
    return (
        f"Hi, {user.username or user.first_name or user.last_name or  f'Anonymous_#{user.id}'}.\n"
        f"For check weather for some city you can send message like: W <your_city>"
    )


@return_bot_message
def weather(update: Update, context: CallbackContext):
    try:
        city = update.effective_message.text.split("W ")[-1].strip()
        current_weather = owm_instance.weather_manager().weather_at_place(city).weather
        temp = round(current_weather.temperature("celsius")["temp"])
        wind = current_weather.wind()["speed"]
        return (
            f"В городе {city} сейчас {current_weather.detailed_status}.\n Температура {temp} ℃.\n"
            f"Скорость ветра составляет {wind} м/с."
        )
    except APIResponseError:
        return "Такого города не существует."
