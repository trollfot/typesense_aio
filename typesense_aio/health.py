import json
from asyncio import sleep
from .requester import Requester


class Health:

    def __init__(self, requester: Requester):
        self.requester = requester
        self.endpoint = "/health"

    async def check(self) -> bool:
        return await self.requester.get(self.endpoint)

    async def wait(self) -> bool:
        try:
            await self.check()
        except:
            await sleep(.2)
            await self.wait()
