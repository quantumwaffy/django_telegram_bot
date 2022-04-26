import functools

import telegram
from telebot.types import User
from telegram import Update
from telegram.ext import CallbackContext

from . import models
from .instance import bot_instance


class UserLoger:
    @staticmethod
    def _update_or_create_user(update: telegram.Update):
        user: User = update.effective_user
        models.TelegramUser.objects.update_or_create(
            telegram_id=user.id,
            defaults={
                "telegram_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            },
        )


def return_bot_message(func):
    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        res = func(update, context)
        return bot_instance.send_message(update.effective_message.chat_id, res)

    return wrapper
