from .requester import Requester


class Debug:

    endpoint: str = "/debug"

    def __init__(self, requester: Requester):
        self.requester = requester

    async def retrieve(self):
        return await self.requester.get(self.endpoint)
