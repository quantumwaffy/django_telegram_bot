from abc import ABC, abstractmethod
from typing import Type

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyMarkup, TelegramObject


class AbstractKeyboardMarkupRender(ABC):
    def __init__(
        self,
        row_count: int,
        choices: list[tuple[str, str]],
        keyboard_markup_class: "Type[ReplyMarkup]" = InlineKeyboardMarkup,
        keyboard_button_class: "Type[TelegramObject]" = InlineKeyboardButton,
    ):
        self._row_count: int = row_count
        self._choices = choices
        self._keyboard_markup_class = keyboard_markup_class
        self._keyboard_button_class = keyboard_button_class

    @abstractmethod
    def _get_button_callback(self, button_callback: str) -> str:
        ...

    @abstractmethod
    def _get_button_label(self, button_label: str) -> str:
        ...

    def _get_buttons_initial(self) -> list[dict[str, str]]:
        return [
            {"text": self._get_button_label(button_label), "callback_data": self._get_button_callback(button_callback)}
            for button_callback, button_label in self._choices
        ]

    def _get_buttons(self) -> list[TelegramObject]:
        return [self._keyboard_button_class(**btn_initial_data) for btn_initial_data in self._get_buttons_initial()]

    def get_markup(self):
        buttons: list[TelegramObject] = self._get_buttons()
        return self._keyboard_markup_class(
            [buttons[i : i + self._row_count] for i in range(0, len(buttons), self._row_count)]
        )
