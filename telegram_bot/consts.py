from enum import Enum

from django.db.models import TextChoices


class BaseMessageResponses(Enum):
    SUCCESS = "Successfully applied"
    ERROR = "An error occurred"


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
