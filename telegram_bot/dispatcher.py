from django.conf import settings
from telegram import ext

from core import command_handlers

from . import commands, consts, utils
from .instance import bot_instance


def setup_dispatcher(dispatcher):
    dispatcher.add_handler(ext.CommandHandler("start", commands.get_start))
    dispatcher.add_handler(ext.CommandHandler("menu", utils.render_menu_keyboard))
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

    dispatcher.add_handler(
        ext.ConversationHandler(
            entry_points=[ext.CallbackQueryHandler(commands.user_settings_callback, pattern=r"^acc$")],
            states={
                consts.INPUT_TIME: [
                    ext.CallbackQueryHandler(
                        commands.CurrencyBeatScheduleHandler(
                            current_state=consts.INPUT_TIME, next_state=consts.SET_TIME
                        ),
                        pattern=r"^bw$",
                    ),
                    ext.CallbackQueryHandler(
                        commands.WeatherBeatScheduleHandler(
                            current_state=consts.INPUT_TIME, next_state=consts.SET_TIME
                        ),
                        pattern=r"^bex$",
                    ),
                ],
                consts.SET_TIME: [
                    ext.MessageHandler(
                        ext.Filters.regex(r"^[\d:\d]+$") & (~ext.Filters.command),
                        handler(current_state=consts.SET_TIME, next_state=ext.ConversationHandler.END),
                    )
                    for handler in [commands.CurrencyBeatScheduleHandler, commands.WeatherBeatScheduleHandler]
                ],
            },
            fallbacks=[
                ext.CommandHandler("cancel", commands.return_to_menu),
                ext.MessageHandler(
                    ~ext.Filters.regex(r"^[\d:\d]+$"), command_handlers.BeatScheduleHandler.send_regex_error
                ),
            ],
        )
    )
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.WeatherDisableBeatScheduleHandler(), pattern=r"^off_w$"))
    dispatcher.add_handler(ext.CallbackQueryHandler(commands.CurrencyDisableBeatScheduleHandler(), pattern=r"^off_ex$"))
    return dispatcher


def run_pooling():
    """Run bot in pooling mode"""
    updater = ext.Updater(settings.TELEGRAM_TOKEN, use_context=True)
    setup_dispatcher(updater.dispatcher)
    updater.start_polling(timeout=123)
    updater.idle()


dispatcher_instance = setup_dispatcher(ext.Dispatcher(bot_instance, update_queue=None, workers=0, use_context=True))
