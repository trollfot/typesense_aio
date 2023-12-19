from .requester import Requester


class Synonym:

    def __init__(self,
                 requester: Requester,
                 collection_name: str,
                 synonym_id: str
                 ):
        self.requester = requester
        self.collection_name = collection_name
        self.synonym_id = synonym_id
        self.endpoint = (
            f"/collections/{collection_name}/synonyms/{synonym_id}"
        )

    async def upsert(self, schema: dict):
        return await self.requester.put(self.endpoint, data=schema)

    async def retrieve(self):
        return await self.requester.get(self.endpoint)

    async def delete(self):
        return await self.requester.delete(self.endpoint)


class Synonyms:

    def __init__(self, requester: Requester, collection_name: str):
        self.requester = requester
        self.collection_name = collection_name
        self.synonyms = {}
        self.endpoint = f"/collections/{collection_name}/synonyms"

    def __getitem__(self, synonym_id):
        if synonym_id not in self.synonyms:
            self.synonyms[synonym_id] = Synonym(
                self.requester,
                self.collection_name,
                synonym_id
            )
        return self.synonyms[synonym_id]

    async def retrieve(self):
        return await self.requester.get(self.endpoint)
