import os

import telegram
from django.db.models import Max, Min
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from core import command_handlers
from core import consts as core_consts
from core import utils as core_utils
from django_telegrambot.settings import STATICFILES_DIRS

from . import consts, forms, utils
from .instance import bot_instance
from .models import ActualCurrencyInfo, TelegramUser


@utils.return_bot_message(parse_mode="html")
def get_start(update: Update, context: CallbackContext):
    user = update.effective_user
    with open(os.path.join(STATICFILES_DIRS[0], "images", "AnimatedSticker.tgs"), "rb") as f:
        bot_instance.send_sticker(update.effective_message.chat_id, f)
    return (
        f"Hi, <b>{user.first_name or user.username or user.last_name or  f'Anonymous_#{user.id}'}</b>!\n"
        f"Type /menu to open the main menu\n"
        f"For morning notifications about weather you can set your location (default: "
        f"{consts.WeatherResponses.DEFAULT_CITY.value}) like:\n<i>/save_city YOUR_CITY</i>\n"
    )


def get_menu(update: Update, context: CallbackContext):
    utils.render_menu_keyboard(update, context)


def return_to_menu(update: Update, context: CallbackContext):
    utils.render_menu_keyboard(update, context)
    return ConversationHandler.END


def get_city_choice(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_message.chat_id, f"Input city name {core_consts.RETURN_MESSAGE_PART}")
    return 0


def get_weather(update: Update, context: CallbackContext):
    city = update.effective_message.text
    context.bot.send_message(update.effective_message.chat_id, utils.get_weather_message(city))
    utils.render_menu_keyboard(update, context)
    return ConversationHandler.END


@utils.return_bot_message()
def set_location(update: Update, context: CallbackContext):
    try:
        city: str = context.args[0].strip()
    except IndexError:
        return consts.WeatherResponses.NO_CHOICE.value
    if not utils.check_weather(city):
        return consts.WeatherResponses.ERROR.value
    try:
        user = TelegramUser.objects.get(telegram_id=update.effective_user.id)
    except (TelegramUser.DoesNotExist, TelegramUser.MultipleObjectsReturned):
        return consts.WeatherResponses.ERROR.value
    user.city_location = city
    user.save()
    return core_consts.BaseMessageResponses.SUCCESS.value


def command_exchange(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Please choose city:",
        reply_markup=core_utils.CityKeyboardMarkupRender(3, consts.CityCallbackChoices.choices).get_markup(),
    )


def city_callback(update: Update, context: CallbackContext):
    context.bot.edit_message_text(
        text="Please choose info type:",
        chat_id=update.effective_user.id,
        message_id=update.callback_query.message.message_id,
        reply_markup=core_utils.CurrencyKeyboardMarkupRender(
            update, 2, consts.CurrencyCallbackChoices.choices
        ).get_markup(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


class CurrencyRateProcessor(command_handlers.BaseHandler):
    update: Update
    context: CallbackContext
    model: ActualCurrencyInfo = ActualCurrencyInfo
    city: str
    info_type: str
    filter_field: str

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        callback_city, callback_operation = self._update.callback_query.data.split("|")
        self.city = dict(consts.CityCallbackChoices.choices).get(callback_city)
        self.info_type = dict(consts.CurrencyCallbackChoices.choices).get(callback_operation)
        self.filter_field = consts.CurrencyCallbackChoices.value_name_dict.get(callback_operation)
        return self._context.bot.send_message(
            self._update.effective_message.chat_id, self._make_response_message(), parse_mode="html"
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
        return self.model.objects.filter(**filter_params).values_list("bank", self.filter_field)

    def _make_response_message(self):
        message = f"<b>{self.city.capitalize()} - {self.info_type}\n</b>"
        for bank, exchange_value in self._get_object_list():
            message += f"{bank}: <i>{exchange_value}</i>\n"
        return message.strip("\n")


class CurrencyBeatScheduleHandler(command_handlers.BeatScheduleHandler):
    _form_class = forms.CurrencyBeatUserSettingsForm


class WeatherBeatScheduleHandler(command_handlers.BeatScheduleHandler):
    _form_class = forms.WeatherBeatUserSettingsForm


class CurrencyDisableBeatScheduleHandler(command_handlers.DisableBeatScheduleHandler):
    _schedule_field = "beat_currency"


class WeatherDisableBeatScheduleHandler(command_handlers.DisableBeatScheduleHandler):
    _schedule_field = "beat_weather"


def user_settings_callback(update: Update, context: CallbackContext):
    context.bot.edit_message_text(
        text="Please choose info type:",
        chat_id=update.effective_user.id,
        message_id=update.callback_query.message.message_id,
        reply_markup=core_utils.BaseKeyboardMarkupRender(2, consts.UserSettingsCallbackChoices.choices).get_markup(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )
    return 0
