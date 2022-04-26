from django.urls import path

from . import views

urlpatterns = [
    path("handlers/", views.TelegramBotHandler.as_view(), name="handlers"),
]
