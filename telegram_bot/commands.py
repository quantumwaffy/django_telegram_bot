import os

from telegram import Update
from telegram.ext import CallbackContext

from django_telegrambot.settings import STATICFILES_DIRS

from . import consts
from .instance import bot_instance
from .models import TelegramUser
from .utils import check_weather, get_weather_message, return_bot_message


@return_bot_message
def command_start(update: Update, context: CallbackContext):
    user = update.effective_user
    with open(os.path.join(STATICFILES_DIRS[0], "images", "AnimatedSticker.tgs"), "rb") as f:
        bot_instance.send_sticker(update.effective_message.chat_id, f)
    return (
        f"Hi, {user.username or user.first_name or user.last_name or  f'Anonymous_#{user.id}'}.\n"
        f"For morning notifications about weather you can set your location like: L <your_city> "
        f"(default: {consts.WeatherResponses.DEFAULT_CITY.value}).\n"
        f"For check weather for some city you can send message like: W <your_city>"
    )


@return_bot_message
def get_weather(update: Update, context: CallbackContext):
    city: str = update.effective_message.text.split("W ")[-1].strip()
    return get_weather_message(city)


@return_bot_message
def set_location(update: Update, context: CallbackContext):
    city: str = update.effective_message.text.split("L ")[-1].strip()
    is_city_exists = bool(check_weather(city))
    if not is_city_exists:
        return consts.WeatherResponses.ERROR.value
    try:
        user = TelegramUser.objects.get(telegram_id=update.effective_user.id)
    except (TelegramUser.DoesNotExist, TelegramUser.MultipleObjectsReturned):
        return consts.WeatherResponses.ERROR.value
    user.city_location = city
    user.save()
    return consts.BaseMessageResponses.SUCCESS.value
