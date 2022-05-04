from django.conf import settings
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    Updater,
)

from . import commands
from .instance import bot_instance


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", commands.get_start))
    dispatcher.add_handler(CommandHandler("menu", commands.get_menu))
    # dispatcher.add_handler(CommandHandler("weather", commands.get_weather, pass_args=True))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(commands.get_city_choice, pattern=r"^w$")],
            states={0: [MessageHandler(Filters.regex(r"^[\D]+$") & (~Filters.command), commands.get_weather)]},
            fallbacks=[CommandHandler("cancel", commands.return_to_menu)],
        )
    )
    dispatcher.add_handler(CommandHandler("save_city", commands.set_location, pass_args=True))
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
