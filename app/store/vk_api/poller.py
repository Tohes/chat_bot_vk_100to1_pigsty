import asyncio
from asyncio import Task
from typing import Optional

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        # self.poll_task = Task(self.poll())

    #     added
    #     self.poll_task.add_done_callback(self._done_callback)

    async def stop(self):

        self.is_running = False
        # changed from
        await self.poll_task
        # # changed to
        # await asyncio.wait([self.poll_task], timeout = 30 )


    async def poll(self):
        if self.store.started:
            await self.store.bots_manager.handle_updates([], "started")
            self.store.started = False
        while self.is_running:
            # сюда вшить инициализацию при рестарте?
            updates = await self.store.vk_api.poll()
            await self.store.bots_manager.handle_updates(updates)