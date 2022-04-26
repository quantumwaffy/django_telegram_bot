# Create your views here.
import json
from typing import Any

import telegram
from django import http
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from telegram_bot.utils import UserLoger

from . import dispatcher, instance


@method_decorator(csrf_exempt, name="dispatch")
class TelegramBotHandler(View, UserLoger):
    def post(self, request: http.HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> http.HttpResponse:
        update: telegram.Update = telegram.Update.de_json(json.loads(request.body), instance.bot_instance)
        self._update_or_create_user(update)
        dispatcher.dispatcher_instance.process_update(update)
        return http.JsonResponse({"status_code": 200, "text": "ok"})

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> http.JsonResponse:
        return http.JsonResponse({"status_code": 200, "text": "is not processed"})
