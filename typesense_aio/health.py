from .requester import Requester


class Health:
    endpoint: str = "/health"

    def __init__(self, requester: Requester):
        self.requester = requester

    async def check(self) -> bool:
        return await self.requester.get(self.endpoint)
