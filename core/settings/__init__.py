import ast
import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

env_file_name = os.environ.get("ENV_FILE", default=".env")
env_file = find_dotenv(filename=env_file_name, raise_error_if_not_found=True)
load_dotenv(env_file)


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(node_or_string=value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


CACHE = get_bool_from_env("CACHE", False)
CACHE_CONFIG = {
    "default": {
        "cache": "aiocache.SimpleMemoryCache",
        "serializer": {"class": "aiocache.serializers.StringSerializer"},
    },
    "redis_alt": {
        "cache": "aiocache.RedisCache",
        "endpoint": os.environ.get("REDIS_HOST", "127.0.0.1"),
        "port": int(os.environ.get("REDIS_PORT", 6379)),
        "timeout": 1,
        "serializer": {"class": "aiocache.serializers.PickleSerializer"},
        "plugins": [{"class": "aiocache.plugins.HitMissRatioPlugin"}, {"class": "aiocache.plugins.TimingPlugin"}],
    },
}

DEBUG = get_bool_from_env("DEBUG", False)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PATH_CORE = os.path.join(BASE_DIR, "core")
PATH_APPS = os.path.join(PATH_CORE, "apps")
PATH_SETTINGS = os.path.join(PATH_CORE, "settings")
PATH_LOGGERS = os.path.join("./logs")

DEFAULT_DIR_FOR_MODELS = "models"
DEFAULT_LIST_SQL_CREATE_TABLES = []
DEFAULT_VAR_SQL_CREATE_TABLES = "LIST_SQL_CREATE_TABLES"
DEFAULT_VAR_ROUTES = "urlpatterns"

ROOT_URLCONF = "core.project.urls"
API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_AUTH_HEADER = "Authorization"
API_PRICES_URL = os.environ.get("API_PRICES_URL", API_BASE_URL)
API_CONTENT_URL = os.environ.get("API_CONTENT_URL", API_BASE_URL)
API_SUPPLIES_URL = os.environ.get("API_SUPPLIES_URL", API_BASE_URL)
API_MARKETPLACE_URL = os.environ.get("API_MARKETPLACE_URL", API_BASE_URL)
API_STATISTICS_URL = os.environ.get("API_STATISTICS_URL", API_BASE_URL)
API_ANALYTICS_URL = os.environ.get("API_ANALYTICS_URL", API_BASE_URL)
API_ADVERT_URL = os.environ.get("API_ADVERT_URL", API_BASE_URL)
API_FEEDBACKS_URL = os.environ.get("API_FEEDBACKS_URL", API_BASE_URL)

# Ключи для тестовой среды
TEST_API_KEY = os.environ.get("TEST_API_KEY")

SANDBOX_API_PRICES_URL = os.environ.get(
    "SANDBOX_API_PRICES_URL", "https://discounts-prices-api-sandbox.wildberries.ru"
)
SANDBOX_API_CONTENT_URL = os.environ.get("SANDBOX_API_CONTENT_URL", "https://content-api-sandbox.wildberries.ru")

SANDBOX_API_STATISTICS_URL = os.environ.get(
    "SANDBOX_API_STATISTICS_URL", "https://statistics-api-sandbox.wildberries.ru"
)
SANDBOX_API_MARKETPLACE_URL = os.environ.get(
    "SANDBOX_API_MARKETPLACE_URL",
)

MIDDLEWARE = [
    # "core.project.middlewares.authentication.jwt_middleware",
]

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {"format": "[%(levelname)s:%(asctime)s] %(message)s"},
    },
    "handlers": {},
    "loggers": {},
}

loggers = {
    "errors": os.path.join(PATH_LOGGERS, "errors.log"),
    "info": os.path.join(PATH_LOGGERS, "info.log"),
}

for path in (PATH_LOGGERS,):
    if not os.path.exists(path):
        try:
            original_umask = os.umask(0)
            os.makedirs(path, mode=0o777)
        finally:
            os.umask(original_umask)

for logger_name, logger_file in loggers.items():
    if not os.path.exists(logger_file):
        with open(logger_file, "w") as f:
            f.write("")

    LOGGING_CONFIG["handlers"] |= {
        logger_name: {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logger_file,
            "level": "DEBUG",
            "formatter": "default_formatter",
            "maxBytes": 30720,  # 30*1024 bytes (30MB)
            "backupCount": 5,
        }
    }

    LOGGING_CONFIG["loggers"] |= {
        logger_name: {
            "handlers": [logger_name],
            "level": "DEBUG",
            "propagate": False,
        },
    }

WEB_APP = {
    "host": os.environ.get("HOST_WEB_APP", "127.0.0.1"),
    "port": os.environ.get("PORT_WEB_APP", "8002"),
}

DATABASES = {
    "default": {
        "host": os.environ.get("HOST_DB_DEF", "127.0.0.1"),
        "port": os.environ.get("PORT_DB_DEF", "5432"),
        "user": os.environ.get("USER_DB_DEF", "postgres"),
        "password": os.environ.get("PASSWORD_DB_DEF", ""),
        "database": os.environ.get("NAME_DB_DEF", ""),
    },
    "test": {
        "host": os.environ.get("HOST_TEST_DEF", "127.0.0.1"),
        "port": os.environ.get("PORT_TEST_DEF", "5432"),
        "user": os.environ.get("USER_TEST_DEF", "postgres"),
        "password": os.environ.get("PASSWORD_TEST_DEF", ""),
        "database": os.environ.get("NAME_TEST_DEF", ""),
    },
}

RABBIT_MQ = {
    "url": os.environ.get("URL_RABBIT_MQ", "amqp://ecom:ecom@127.0.0.1/ms_marketplaces"),
    "host": os.environ.get("HOST_RABBIT_MQ", "172.17.0.1"),
    "port": os.environ.get("PORT_RABBIT_MQ", "15672"),
    "user_name": os.environ.get("USER_RABBIT_MQ", ""),
    "password": os.environ.get("PASSWORD_RABBIT_MQ", ""),
    "vhost": os.environ.get("VHOST_RABBIT_MQ", "ms_marketplaces"),
    "queue": os.environ.get("QUEUE_RABBIT_MQ", "queue"),
    "exchange": os.environ.get("EXCHANGE_RABBIT_MQ", "ms_exchange"),
}

PLATFORM = {
    "url_auth": os.environ.get("URL_AUTH", "http://127.0.0.1:8000/v1/webhook/authenticate/"),
    "url_webhook": os.environ.get("URL_WEBHOOK_PLATFORM", "http://127.0.0.1:8000/v1/webhook/"),
    "url_relations_products": os.environ.get(
        "URL_RELATIONS_PRODUCTS",
        "http://127.0.0.1:8000/v1/marketplaces/%s/relationships/",
    ),
    "url_warehouses_fbo": os.environ.get(
        "URL_WAREHOUSES_FBO",
        "http://127.0.0.1:8000/v1/marketplaces/%s/warehouses_fbo/",
    ),
    "url_marketplaces": os.environ.get(
        "URL_MARKETPLACES",
        "http://127.0.0.1:8000/v1/marketplaces/",
    ),
}

DEFAULT_DATABASE = os.environ.get("DEFAULT_DATABASE", "default")
TEST_DATABASE = os.environ.get("TEST_DATABASE", "test")
DEFAULT_DIR_FOR_MODELS = os.environ.get("DEFAULT_DIR_FOR_MODELS", "models")
ROOT_URLCONF = os.environ.get("ROOT_URLCONF", "core.project.urls")
MAX_COUNT_REPEAT_REQUESTS = int(os.environ.get("MAX_COUNT_REPEAT_REQUESTS", 3))
CONSUMER_HANDLER = os.environ.get("CONSUMER_HANDLER", "core.apps.basic.services.handlers.CommonHandler")
LIST_SQL_CREATE_TABLES = ("LIST_SQL_CREATE_TABLES",)

# RABBIT_MQ
CODE_CONSUMER = os.environ.get("CODE_CONSUMER", "consumer")
CODE_PUBLISHER = os.environ.get("CODE_PUBLISHER", "publisher")
STOCK_QUEUE_PUBLISHER = os.environ.get("STOCK_QUEUE_PUBLISHER", "stock")


SCHEDULE = {
    # "test_too": {"task": "core.project.services.scheduler.common.test_too", "schedule": 1},
    "bulk_import_orders": {"task": "core.apps.basic.services.handlers.orders.bulk_import_orders", "schedule": 600},
}

EMAIL_SUPERUSER_PLATFORM = os.environ.get("EMAIL_SUPERUSER_PLATFORM", "")
PASSWORD_SUPERUSER_PLATFORM = os.environ.get("PASSWORD_SUPERUSER_PLATFORM", "")
