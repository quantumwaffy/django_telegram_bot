from django.conf import settings
from telegram import ext

from . import commands
from .instance import bot_instance


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(ext.CommandHandler("start", commands.get_start))
    dispatcher.add_handler(ext.CommandHandler("menu", commands.get_menu))
    dispatcher.add_handler(
        ext.ConversationHandler(
            entry_points=[ext.CallbackQueryHandler(commands.get_city_choice, pattern=r"^w$")],
            states={
                0: [ext.MessageHandler(ext.Filters.regex(r"^[\D]+$") & (~ext.Filters.command), commands.get_weather)]
            },
            fallbacks=[ext.CommandHandler("cancel", commands.return_to_menu)],
        )
    )
    dispatcher.add_handler(ext.CommandHandler("save_city", commands.set_location, pass_args=True))
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.command_exchange, pattern=r"^ex$"))
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.city_callback, pattern=r"^city\d$"))
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.CurrencyRateProcessor(), pattern=r"^city\d|_c\d$"))
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.city_callback, pattern=r"^city\d$"))
    return dispatcher


def run_pooling():
    """Run bot in pooling mode"""
    updater = ext.Updater(settings.TELEGRAM_TOKEN, use_context=True)
    setup_dispatcher(updater.dispatcher)
    updater.start_polling(timeout=123)
    updater.idle()


dispatcher_instance = setup_dispatcher(ext.Dispatcher(bot_instance, update_queue=None, workers=0, use_context=True))
