import logging

# from core.project.services.requesters import Requester
from core.project.services.requesters import AppRequester


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class WarehouseRequester(AppRequester):
    pass
