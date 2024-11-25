import logging

from core.project.services.requesters import AppRequester


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class SalesRequester(AppRequester):
    pass


class SalesReportRequester(AppRequester):
    pass
