import functools

from pyowm.commons.exceptions import APIResponseError
from telegram import Update, User
from telegram.ext import CallbackContext

from core import utils as core_utils

from . import consts, models
from .instance import bot_instance, owm_instance


class UserLoger:
    @staticmethod
    def _update_or_create_user(update: Update):
        user: User = update.effective_user
        obj, created = models.TelegramUser.objects.update_or_create(
            telegram_id=user.id,
            defaults={
                "telegram_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            },
        )
        models.Message.objects.create(telegram_user=obj, text=update.effective_message.text)
        models.TelegramUserSettings.objects.create(telegram_user=obj) if created else None


# Takes args and kwargs for bot method send_message
def return_bot_message(*args, **kwargs):
    def inner(func):
        @functools.wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            res = func(update, context)
            return bot_instance.send_message(update.effective_message.chat_id, res, *args, **kwargs)

        return wrapper

    return inner


def check_weather(city: str) -> dict:
    try:
        current_weather = owm_instance.weather_manager().weather_at_place(city).weather
    except APIResponseError:
        return {}
    else:
        return {
            "status": current_weather.detailed_status,
            "temperature": round(current_weather.temperature("celsius")["temp"]),
            "wind": current_weather.wind()["speed"],
        }


def get_weather_message(city: str) -> str:
    weather_info = check_weather(city)
    if weather_info:
        return (
            f"It's {weather_info.get('status')} in {city} right now.\n"
            f"Temperature of {weather_info.get('temperature')} ℃.\n"
            f"Wind speed of {weather_info.get('wind')} m/s."
        )
    else:
        return consts.WeatherResponses.ERROR.value


def render_menu_keyboard(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Please make a choice:",
        reply_markup=core_utils.BaseKeyboardMarkupRender(2, consts.MainMenuCallbackChoices.choices).get_markup(),
    )
