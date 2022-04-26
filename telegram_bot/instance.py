import pyowm
import telegram
from pyowm.utils.config import get_default_config

from django_telegrambot import settings

bot_instance = telegram.Bot(settings.TELEGRAM_TOKEN)

config_dict = get_default_config()
config_dict["language"] = "ru"
owm_instance = pyowm.OWM(settings.PYOWM_TOKEN, config_dict)
