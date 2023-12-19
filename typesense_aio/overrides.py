from .requester import Requester


class Override:

    def __init__(self,
                 requester: Requester,
                 collection_name: str,
                 override_id: str
                 ):
        self.requester = requester
        self.endpoint: str = (
            f"/collections/{collection_name}/overrides/{override_id}"
        )

    async def retrieve(self):
        return await self.requester.get(self.endpoint)

    async def delete(self):
        return await self.requester.delete(self.endpoint)

    async def upsert(self, schema: dict):
        return await self.requester.put(self.endpoint, data=schema)


class Overrides:

    def __init__(self, requester: Requester, collection_name: str):
        self.requester = requester
        self.collection_name = collection_name
        self.overrides = {}
        self.endpoint: str = f"/collections/{collection_name}/overrides"

    def __getitem__(self, override_id):
        if override_id not in self.overrides:
            self.overrides[override_id] = Override(
                self.requester,
                self.collection_name,
                override_id
            )
        return self.overrides[override_id]

    async def retrieve(self):
        return await self.requester.get(self.endpoint)
