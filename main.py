from aiohttp import web
from icecream import ic
from prometheus_async import aio

from core.project.conf import settings
from core.project.db.connect import destroy_database_pool, create_database_pool
from core.project.db.execute_migrations import create_tables
from core.project.message_manager.consumers import main_consumer
from core.project.message_manager.publisher import main_publisher
from core.project.services.scheduler.common import scheduler
from core.project.utils import client_session, client_cache

ic.configureOutput(includeContext=True, contextAbsPath=True)


def main():
    app = web.Application(middlewares=settings.MIDDLEWARE)
    if settings.CACHE:
        app.on_startup.append(client_cache)
    app.on_startup.append(create_database_pool)
    app.on_startup.append(create_tables)

    app.on_cleanup.append(destroy_database_pool)
    app.add_routes(settings.ROUTES)
    app.router.add_get("/metrics", aio.web.server_stats)
    app.cleanup_ctx.append(client_session)
    app.cleanup_ctx.append(scheduler)
    app.cleanup_ctx.append(main_consumer)
    app.cleanup_ctx.append(main_publisher)

    web.run_app(app, host=settings.WEB_APP.get("host", "localhost"), port=settings.WEB_APP.get("port", "8080"))


main()
