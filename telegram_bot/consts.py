from enum import Enum

from django.db.models import TextChoices


class BaseMessageResponses(Enum):
    SUCCESS = "Successfully applied"
    ERROR = "An error occurred"


class WeatherResponses(Enum):
    DEFAULT_CITY = "Minsk"
    ERROR = "There is no such city"


class CurrencyCallbackChoices(TextChoices):
    ALL = "All exchange rates", "c0"
    ALL_BEST = "All best exchange rates", "c1"
    BEST_USD_BUY = "Best buy $", "c2"
    BEST_USD_SALE = "Best sale $", "c3"
    BEST_EURO_BUY = "Best buy €", "c4"
    BEST_EURO_SALE = "Best sale €", "c5"
    BEST_RUB_BUY = "Best buy ₽", "c6"
    BEST_RUB_SALE = "Best sale ₽", "c7"
    BEST_EURO_TO_USD_BUY = "Best buy $ from €", "c8"
    BEST_EURO_TO_USD_SALE = "Best sale $ from €", "c9"


class CityCallbackChoices(TextChoices):
    MINSK = "minsk", "city0"
    BREST = "brest", "city1"
    VITEBSK = "vitebsk", "city2"
    GOMEL = "gomel", "city3"
    GRODNO = "grodno", "city4"
    MOGILEV = "mogilev", "city5"
