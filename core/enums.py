from enum import Enum, auto

class RequestParseStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ONGOING = "ongoing"

class LogType(Enum):
    INFO = auto()
    ERROR = auto()