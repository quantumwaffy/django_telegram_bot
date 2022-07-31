from enum import Enum

from django.db.models import TextChoices

SOURCE = "https://myfin.by/currency-old/"


class WeatherResponses(Enum):
    DEFAULT_CITY = "Minsk"
    ERROR = "There is no such city"
    NO_CHOICE = "Not selected city"


class CurrencyCallbackChoices(TextChoices):
    usd_buy = "c0", "Best buy $"
    usd_sell = "c1", "Best sale $"
    euro_buy = "c2", "Best buy €"
    euro_sell = "c3", "Best sale €"
    rub_buy = "c4", "Best buy ₽"
    rub_sell = "c5", "Best sale ₽"
    usd_buy_from_euro = "c6", "Best buy $ from €"
    usd_sell_from_euro = "c7", "Best sale $ from €"

    @classmethod
    @property
    def value_name_dict(cls) -> dict[str, str]:
        return {value: name for value, name in zip(cls.values, cls.names)}


class CityCallbackChoices(TextChoices):
    MINSK = "city0", "minsk"
    BREST = "city1", "brest"
    VITEBSK = "city2", "vitebsk"
    GOMEL = "city3", "gomel"
    GRODNO = "city4", "grodno"
    MOGILEV = "city5", "mogilev"


class MainMenuCallbackChoices(TextChoices):
    WEATHER = "w", "Check weather"
    EXCHANGE = "ex", "Check best currency rate"
    ACCOUNT = "acc", "User settings"


class UserSettingsCallbackChoices(TextChoices):
    BEAT_WEATHER = "bw", "Weather schedule"
    BEAT_EXCHANGE = "bex", "Currency schedule"
    OFF_BEAT_WEATHER = "off_w", "Disable weather"
    OFF_BEAT_CURRENCY = "off_ex", "Disable currency"


WEATHER_MINUTE_STEP_BEAT: int = 30
CURRENCY_MINUTE_STEP_BEAT: int = 30

# BEAT CONVERSATION STATES
INPUT_TIME, SET_TIME = range(2)
