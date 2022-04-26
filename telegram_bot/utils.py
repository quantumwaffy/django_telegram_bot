import functools

from telegram import Update, User
from telegram.ext import CallbackContext

from . import models
from .instance import bot_instance


class UserLoger:
    @staticmethod
    def _update_or_create_user(update: Update):
        user: User = update.effective_user
        obj, _ = models.TelegramUser.objects.update_or_create(
            telegram_id=user.id,
            defaults={
                "telegram_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            },
        )
        models.Message.objects.create(telegram_user=obj, text=update.effective_message.text)


def return_bot_message(func):
    @functools.wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        res = func(update, context)
        return bot_instance.send_message(update.effective_message.chat_id, res)

    return wrapper
