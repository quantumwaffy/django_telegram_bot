from telegram import Update

from . import base


class BaseKeyboardMarkupRender(base.AbstractKeyboardMarkupRender):
    def _get_button_callback(self, button_callback: str) -> str:
        return button_callback

    def _get_button_label(self, button_label: str) -> str:
        return button_label


class CityKeyboardMarkupRender(BaseKeyboardMarkupRender):
    def _get_button_label(self, button_label: str) -> str:
        return button_label.capitalize()


class CurrencyKeyboardMarkupRender(BaseKeyboardMarkupRender):
    def __init__(self, update: Update, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update: Update = update

    def _get_button_callback(self, button_callback: str) -> str:
        return f"{self._update.callback_query.data}|{button_callback}"
