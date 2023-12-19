import httpx
from typing import Dict, Optional, Generic, TypeVar
from .requester import Requester
from .documents import Documents
from .types import CollectionDict
from .synonyms import Synonyms
from .overrides import Overrides


T = TypeVar("T")


class Collection(Generic[T]):

    def __init__(self, requester: Requester, name: str):
        self.name = name
        self.requester = requester
        self.documents: Documents[T] = Documents(requester, name)
        self.synonyms: Synonyms = Synonyms(requester, name)
        self.overrides: Overrides = Overrides(requester, name)
        self.endpoint = f"/collections/{self.name}"

    async def retrieve(self) -> Optional[CollectionDict]:
        try:
            return await self.requester.get(self.endpoint)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.NOT_FOUND:
                return None
            raise e

    async def delete(self):
        return await self.requester.delete(self.endpoint)


class Collections:

    endpoint: str = "/collections"

    def __init__(self, requester: Requester):
        self.requester = requester
        self.collections: Dict[str, Collection] = {}

    def __getitem__(self, collection_name: str) -> Collection:
        if collection_name not in self.collections:
            self.collections[collection_name] = Collection(
                self.requester, collection_name
            )
        return self.collections.get(collection_name)

    async def create(self, schema: CollectionDict) -> CollectionDict:
        return await self.requester.post(self.endpoint, data=schema)

    async def retrieve(self) -> CollectionDict:
        return await self.requester.get(self.endpoint)
