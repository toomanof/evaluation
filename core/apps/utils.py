import aiohttp
from abc import ABC
from sqlalchemy import text
from sqlalchemy.dialects import postgresql


class BaseExternalClient(ABC):
    async def get(
        self,
        url: str,
    ):
        url = f"{self.base_url}{url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                return resp

    async def post(self, url: str, data=None):
        url = f"{self.base_url}{url}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                return resp


def get_postgresql_value(value):
    return str(
        text(text=":x")
        .bindparams(x=value)
        .compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
