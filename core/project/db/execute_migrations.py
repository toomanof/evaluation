from aiohttp.web_app import Application
from asyncpg import Pool

from core.project.conf import settings


async def create_tables(app: Application):
    pool: Pool = app[settings.DEFAULT_DATABASE]
    for statement in settings.DEFAULT_LIST_SQL_CREATE_TABLES:
        await pool.execute(statement)
