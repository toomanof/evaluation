import asyncio
import traceback
from asyncio import sleep
from datetime import datetime

from aiohttp.web import Application
from icecream import ic

from core.project.conf import settings
from core.project.utils import import_string


async def test_too(app: Application):
    print("RUN test_too")


class Scheduler:
    app: Application

    async def __call__(self, app: Application, *args, **kwargs):
        self.app = app
        self.app["background_tasks"] = set()
        self.create_background_tasks()
        yield
        # self.cancel_background_tasks()

    @staticmethod
    async def background_task(app: Application):
        start_timer = datetime.now()
        print("Start background_tasks")
        while True:
            for key, val in settings.SCHEDULE.items():
                val["run_task"] = True
                method = import_string(val["task"])

                time_now = datetime.now()
                diff = (time_now - start_timer).seconds
                if diff % val["schedule"] == 0:
                    if val["run_task"]:
                        try:
                            await method(app=app)
                        except Exception as err:
                            ic(err, traceback.format_exc())

                        val["run_task"] = False
                else:
                    val["run_task"] = True
            await sleep(1)

    def create_background_tasks(self):
        self.app["background_tasks"].add(asyncio.create_task(self.background_task(self.app)))

    def cancel_background_tasks(self):
        for task in self.app["background_tasks"]:
            task.cancel()


scheduler = Scheduler()
