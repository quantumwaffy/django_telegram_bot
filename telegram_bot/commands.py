from pyowm.commons.exceptions import APIResponseError
from telegram import Update
from telegram.ext import CallbackContext

from .instance import owm_instance
from .utils import return_bot_message


@return_bot_message
def command_start(update: Update, context: CallbackContext):
    user = update.effective_user
    return f"Hi, {user.username or f'Anonymous_#{user.id}'}"


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
