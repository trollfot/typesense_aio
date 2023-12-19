from .requester import Requester


class MultiSearch:

    endpoint: str = '/multi_search'

    def __init__(self, requester: Requester):
        self.requester = requester

    async def perform(self, search_queries, params: dict | None = None):
        return await self.requester.post(
            self.endpoint,
            data=search_queries,
            params=params
        )
