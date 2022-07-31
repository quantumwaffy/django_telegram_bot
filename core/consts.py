from enum import Enum


class BaseMessageResponses(Enum):
    SUCCESS = "Successfully applied"
    ERROR = "An error occurred"


RETURN_MESSAGE_PART: str = "or type /cancel to return:"
