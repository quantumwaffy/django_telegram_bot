import os

import telegram
from django.db.models import Max, Min
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from django_telegrambot.settings import STATICFILES_DIRS

from . import consts
from .instance import bot_instance
from .models import ActualCurrencyInfo, TelegramUser
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
    buttons = [
        InlineKeyboardButton(label, callback_data=callback) for callback, label in consts.CityCallbackChoices.choices
    ]
    keyboard = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    update.message.reply_text("Please choose city:", reply_markup=InlineKeyboardMarkup(keyboard))


def city_callback(update: Update, context: CallbackContext):
    buttons = [
        InlineKeyboardButton(label, callback_data=f"{update.callback_query.data}|{next_callback}")
        for next_callback, label in consts.CurrencyCallbackChoices.choices
    ]
    keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    context.bot.edit_message_text(
        text="Please choose info type:",
        chat_id=update.effective_user.id,
        message_id=update.callback_query.message.message_id,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


class CurrencyRateProcessor:
    update: Update
    context: CallbackContext
    model: ActualCurrencyInfo = ActualCurrencyInfo
    city: str
    info_type: str
    filter_field: str

    def __call__(self, *args, **kwargs):
        self.update, self.context = args
        callback_city, callback_operation = self.update.callback_query.data.split("|")
        self.city = dict(consts.CityCallbackChoices.choices).get(callback_city)
        self.info_type = dict(consts.CurrencyCallbackChoices.choices).get(callback_operation)
        self.filter_field = consts.CurrencyCallbackChoices.value_name_dict.get(callback_operation)
        return self.context.bot.send_message(
            self.update.effective_message.chat_id, self._make_response_message(), parse_mode="html"
        )

    def _get_object_list(self):
        filter_params = {"city": self.city}
        if "buy" in self.filter_field:
            aggregate_func = Max(self.filter_field)
            aggregated_key = f"{self.filter_field}__max"
        else:
            aggregate_func = Min(self.filter_field)
            aggregated_key = f"{self.filter_field}__min"
        filter_params.update(
            {
                self.filter_field: self.model.objects.filter(**filter_params)
                .aggregate(aggregate_func)
                .get(aggregated_key)
            }
        )
        return self.model.objects.filter(**filter_params).values_list("bank", "usd_buy")

    def _make_response_message(self):
        message = f"<b>{self.city} - {self.info_type}\n</b>"
        for bank, exchange_value in self._get_object_list():
            message += f"{bank}: <i>{exchange_value}</i>\n"
        return message.strip("\n")
