import sys
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from core.apps.tests.test_fetcher_component.routes_for_fetcher_tests import fetcher_routes

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PATH_CORE = os.path.join(BASE_DIR, "core")
PATH_TEST_SERV = os.path.join(PATH_CORE, "tests")
sys.path.insert(0, PATH_CORE)
sys.path.insert(0, PATH_TEST_SERV)

env_file = find_dotenv(filename="env_tests", raise_error_if_not_found=True)
load_dotenv(env_file)

from aiohttp import web  # noqa
from src.routers import (  # noqa
    prices_and_discounts_router,
    content_router,
    suppliers_router,
    statistics_router,
    common_router,
)  # noqa

app = web.Application()
app.add_routes(prices_and_discounts_router)
app.add_routes(content_router)
app.add_routes(suppliers_router)
app.add_routes(statistics_router)
app.add_routes(content_router)
app.add_routes(common_router)
app.add_routes(fetcher_routes)

#
if __name__ == "__main__":
    web.run_app(app=app, port=8083, host="localhost")
