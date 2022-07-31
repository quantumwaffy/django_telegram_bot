import datetime
from typing import NoReturn, Optional

from django import forms as dj_forms
from django.db import models as dj_models
from telegram.ext import ConversationHandler

from telegram_bot import models as tg_models

from . import consts


class BaseHandler:
    def __call__(self, *args, **kwargs):
        self._update, self._context = args


class BaseBeatScheduleHandler(BaseHandler):
    _model: dj_models.Model = tg_models.TelegramUserSettings

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self._user_settings_instance: dj_models.Model = self._model.objects.get(
            telegram_user__telegram_id=self._update.effective_user.id
        )

    def _send_message(self, msg: str) -> NoReturn:
        self._context.bot.send_message(self._update.effective_message.chat_id, msg)


class BeatScheduleHandler(BaseBeatScheduleHandler):
    _form_class: dj_forms.ModelForm
    _input_message: str = f"Input time (hh:mm) {consts.RETURN_MESSAGE_PART}"
    _regex_error: str = (
        f"{consts.BaseMessageResponses.ERROR.value}\nInput by represented format {consts.RETURN_MESSAGE_PART}"
    )

    def __init__(self, current_state: int, next_state: int):
        self._next_state = next_state
        self._current_state = current_state

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        if self._next_state != ConversationHandler.END:
            return self._get_user_input()
        self._message: str = self._update.effective_message.text
        self._main_form_class_field: str = self._form_class.Meta.fields[0]
        return self._next_state if self._is_time_installed() else self._get_user_input(is_repeat=True)

    def _is_time_installed(self) -> bool:
        form: dj_forms.ModelForm = self._form_class(
            {self._main_form_class_field: self._message}, instance=self._user_settings_instance
        )
        if form.is_valid():
            form.save()
            self._send_message(consts.BaseMessageResponses.SUCCESS.value)
            return True
        self._send_message(f"{consts.BaseMessageResponses.ERROR.value}:\n{form.get_error_message()}")
        return False

    def _get_user_input(self, is_repeat: bool = False) -> int:
        self._send_message(self._input_message)
        return self._current_state if is_repeat else self._next_state

    @classmethod
    def send_regex_error(cls, *args) -> NoReturn:
        update, context = args
        context.bot.send_message(update.effective_message.chat_id, cls._regex_error)


class DisableBeatScheduleHandler(BaseBeatScheduleHandler):
    _schedule_field: str
    _success_msg_part: str = " disabled"
    _warning_msg_part: str = f" have already been{_success_msg_part} or not set"

    def __call__(self, *args, **kwargs) -> NoReturn:
        super().__call__(*args, **kwargs)
        self._human_field_name: str = self._model._meta.get_field(self._schedule_field).verbose_name
        return self._disable_beat()

    def _disable_beat(self) -> NoReturn:
        current_value: Optional[datetime.time] = getattr(self._user_settings_instance, self._schedule_field)
        if current_value:
            setattr(self._user_settings_instance, self._schedule_field, None)
            self._user_settings_instance.save()
            return self._send_message(self._human_field_name + self._success_msg_part)
        return self._send_message(self._human_field_name + self._warning_msg_part)
