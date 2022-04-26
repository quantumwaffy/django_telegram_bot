from enum import Enum


class BaseMessageResponses(Enum):
    SUCCESS = "Successfully applied"
    ERROR = "An error occurred"


class WeatherResponses(Enum):
    DEFAULT_CITY = "Minsk"
    ERROR = "There is no such city"
