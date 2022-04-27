import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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
        f"For morning notifications about weather you can set your location like:\nL <your_city> "
        f"(default: {consts.WeatherResponses.DEFAULT_CITY.value}).\n"
        f"For check weather for some city you can send message like:\nW <your_city>"
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


def command_exchange(update: Update, context: CallbackContext):
    city_data = consts.CityCallbackChoices.choices
    city_data_half_len = round(len(city_data) / 2)
    keyboard = [
        [InlineKeyboardButton(label, callback_data=callback) for label, callback in city_data[part]]
        for part in [slice(city_data_half_len), slice(city_data_half_len, None)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please choose city:", reply_markup=reply_markup)


def city_callback(update: Update, context: CallbackContext):
    ...


class CurrencyRateProcessor:
    update: Update
    context: CallbackContext

    def __call__(self, *args, **kwargs):
        self.update, self.context = args
        return 1
