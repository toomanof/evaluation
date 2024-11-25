import asyncpg
from aiohttp.web_app import Application
from asyncpg.pool import Pool

from core.project.conf import settings


async def create_database_pool(app: Application):
    """
    Создание пула подключения к базе данных
    """
    print("Создается пул подключений.")
    database = settings.DATABASES.get(settings.DEFAULT_DATABASE, {})
    pool = await asyncpg.create_pool(
        host=database.get("host"),
        port=database.get("port"),
        user=database.get("user"),
        database=database.get("database"),
        password=database.get("password"),
    )

    app[settings.DEFAULT_DATABASE] = pool
    print("Пул подключений создан")


async def destroy_database_pool(app: Application):
    """
    Уничтожение пула подключения к базе данных
    """
    print("Уничтожается пул подключений.")
    pool: Pool = app[settings.DEFAULT_DATABASE]
    await pool.close()


async def create_test_database_pool(app: Application):
    """
    Создание пула подключения к базе данных
    """
    print("Создается пул подключений.")
    database = settings.DATABASES.get(settings.TEST_DATABASE, {})
    pool = await asyncpg.create_pool(
        host=database.get("host"),
        port=database.get("port"),
        user=database.get("user"),
        database=database.get("database"),
        password=database.get("password"),
    )

    app[settings.DEFAULT_DATABASE] = pool
    print("Пул подключений создан.")


async def create_test_database(app: Application):
    pool: Pool = app[settings.DEFAULT_DATABASE]
    database = settings.DATABASES.get(settings.TEST_DATABASE, {})
    db = database.get("database", "")
    user = database.get("user", "")
    await pool.execute(f"CREATE DATABASE {db} OWNER {user};")


async def drop_test_database(app: Application):
    pool: Pool = app[settings.DEFAULT_DATABASE]
    database = settings.DATABASES.get(settings.TEST_DATABASE, {})
    db = database.get("database", "")
    await pool.execute(f"DROP DATABASE {db};")
