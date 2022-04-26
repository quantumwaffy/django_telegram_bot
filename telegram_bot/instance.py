import pyowm
import telegram

from django_telegrambot import settings

bot_instance = telegram.Bot(settings.TELEGRAM_TOKEN)

owm_instance = pyowm.OWM(settings.PYOWM_TOKEN)
