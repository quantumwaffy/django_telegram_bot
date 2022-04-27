from django.conf import settings
from telegram.ext import CallbackQueryHandler, CommandHandler, Dispatcher, Filters, MessageHandler, Updater

from . import commands
from .instance import bot_instance


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", commands.command_start))
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^W\s\w+"), commands.get_weather))
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^L\s\w+"), commands.set_location))
    dispatcher.add_handler(CommandHandler("exchange", commands.command_exchange))
    dispatcher.add_handler(CallbackQueryHandler(commands.city_callback, pattern=r"^city\d$"))
    dispatcher.add_handler(CallbackQueryHandler(commands.CurrencyRateProcessor(), pattern=r"^city\d|_c\d$"))
    return dispatcher


def run_pooling():
    """Run bot in pooling mode"""
    updater = Updater(settings.TELEGRAM_TOKEN, use_context=True)
    setup_dispatcher(updater.dispatcher)
    updater.start_polling(timeout=123)
    updater.idle()


dispatcher_instance = setup_dispatcher(Dispatcher(bot_instance, update_queue=None, workers=0, use_context=True))
