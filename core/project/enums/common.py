from enum import Enum


class SettingsInDataBase(Enum):
    LAST_FETCH_CAMPAIGNS = "LAST_FETCH_CAMPAIGNS"
    LAST_FETCH_WAREHOUSES = "LAST_FETCH_WAREHOUSES"
    LAST_FETCH_STOCKS = "LAST_FETCH_STOCKS"
    LAST_FETCH_STATISTICS = "LAST_FETCH_STATISTICS"
    LAST_FETCH_ORDERS = "LAST_FETCH_ORDERS"
    LAST_FETCH_SALES = "LAST_FETCH_SALES"


class TypeStatusResponse(Enum):
    POSITIVE = True
    NEGATIVE = False


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [(i, i.value) for i in cls]

    def __repr__(self):
        return f"{self.value}"

    def __str__(self):
        return f"{self.value}"


class RequestMethod(ChoiceEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class StatusTask(ChoiceEnum):
    PROGRESS = "progress"
    START = "start"
    FINISH = "finish"
    ERROR = "error"


class StatusNotification(ChoiceEnum):
    SUCCESS = "success"
    ERROR = "error"
    MARKETPLACE_ERROR = "marketplace_error"
    INFO = "info"
    WARNING = "warning"


class TypeMsg(ChoiceEnum):
    NOTIFICATION = "notification"
    TASK = "task"


class CodeNotification(ChoiceEnum):
    ERROR = "notifications.import.error"
    STARTED = "notifications.import.started"
    FINISHED = "notifications.import.finished"


class RequestMethod(ChoiceEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
