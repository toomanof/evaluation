from aiohttp.web import HTTPException


class InvalidRequestFormatContent(HTTPException):
    status_code = 400


class InvalidQueryParamsContent(HTTPException):
    status_code = 400


class RouterIsDeprecated(HTTPException):
    status_code = 500


class Unauthorized(HTTPException):
    status_code = 401


class TooManyRetries(HTTPException):
    status_code = 429


class ServerUnavailable(HTTPException):
    status_code = 500
