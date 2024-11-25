from datetime import datetime, timezone

from aiohttp import web_exceptions

FORMAT_DATE = "%m.%d.%Y %H:%M:%S"
DATE_TEMPLATE_dmY = "%d-%m-%Y"
DATE_TEMPLATE_Ymd = "%Y-%m-%d"
DATETIME_TEMPLATE_UTC = f"{DATE_TEMPLATE_Ymd}T%H:%M:%SZ"
DATETIME_TEMPLATE_MSC = f"{DATE_TEMPLATE_Ymd}T%H:%M:%S"

AIOHTTP_EXCEPTIONS = {
    200: web_exceptions.HTTPOk,
    201: web_exceptions.HTTPCreated,
    202: web_exceptions.HTTPAccepted,
    203: web_exceptions.HTTPNonAuthoritativeInformation,
    204: web_exceptions.HTTPNoContent,
    205: web_exceptions.HTTPResetContent,
    206: web_exceptions.HTTPPartialContent,
    304: web_exceptions.HTTPNotModified,
    # HTTPMove
    300: web_exceptions.HTTPMultipleChoices,
    301: web_exceptions.HTTPMovedPermanently,
    302: web_exceptions.HTTPFound,
    303: web_exceptions.HTTPSeeOther,
    305: web_exceptions.HTTPUseProxy,
    307: web_exceptions.HTTPTemporaryRedirect,
    308: web_exceptions.HTTPPermanentRedirect,
    # HTTPClientError
    400: web_exceptions.HTTPBadRequest,
    401: web_exceptions.HTTPUnauthorized,
    402: web_exceptions.HTTPPaymentRequired,
    403: web_exceptions.HTTPForbidden,
    404: web_exceptions.HTTPNotFound,
    405: web_exceptions.HTTPMethodNotAllowed,
    406: web_exceptions.HTTPNotAcceptable,
    407: web_exceptions.HTTPProxyAuthenticationRequired,
    408: web_exceptions.HTTPRequestTimeout,
    409: web_exceptions.HTTPConflict,
    410: web_exceptions.HTTPGone,
    411: web_exceptions.HTTPLengthRequired,
    412: web_exceptions.HTTPPreconditionFailed,
    413: web_exceptions.HTTPRequestEntityTooLarge,
    414: web_exceptions.HTTPRequestURITooLong,
    415: web_exceptions.HTTPUnsupportedMediaType,
    416: web_exceptions.HTTPRequestRangeNotSatisfiable,
    417: web_exceptions.HTTPExpectationFailed,
    421: web_exceptions.HTTPMisdirectedRequest,
    422: web_exceptions.HTTPUnprocessableEntity,
    424: web_exceptions.HTTPFailedDependency,
    426: web_exceptions.HTTPUpgradeRequired,
    428: web_exceptions.HTTPPreconditionRequired,
    429: web_exceptions.HTTPTooManyRequests,
    431: web_exceptions.HTTPRequestHeaderFieldsTooLarge,
    451: web_exceptions.HTTPUnavailableForLegalReasons,
    # HTTPServerError
    500: web_exceptions.HTTPInternalServerError,
    501: web_exceptions.HTTPNotImplemented,
    502: web_exceptions.HTTPBadGateway,
    503: web_exceptions.HTTPServiceUnavailable,
    504: web_exceptions.HTTPGatewayTimeout,
    505: web_exceptions.HTTPVersionNotSupported,
    506: web_exceptions.HTTPVariantAlsoNegotiates,
    507: web_exceptions.HTTPInsufficientStorage,
    510: web_exceptions.HTTPNotExtended,
    511: web_exceptions.HTTPNetworkAuthenticationRequired,
}
CONDITION_PREFIX = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<="}

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24
ONE_HUNDRED_SECONDS = 100

J2000 = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
