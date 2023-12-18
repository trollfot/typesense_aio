import pytest
from typesense_aio.collections import Collection
from typing import List, TypedDict


class AppleType(TypedDict):
    id: str
    timestamp: int
    name: str
    color: str


testing_documents: List[AppleType] = [
    {
        "id": "id1",
        "timestamp": 12341,
        "name": "Pink Pearl",
        "color": "pink"
    },
    {
        "id": "id2",
        "timestamp": 12342,
        "name": "Ambrosia",
        "color": "red"
    },
    {
        "id": "id3",
        "timestamp": 12343,
        "name": "Redlove Apples",
        "color": "red"
    },
    {
        "id": "id4",
        "timestamp": 12344,
        "name": "Macoun Apple",
        "color": "red"
    },
    {
        "id": "id5",
        "timestamp": 12345,
        "name": "Grimes Golden",
        "color": "yellow"
    },
    {
        "id": "id6",
        "timestamp": 12346,
        "name": "Opal",
        "color": "yellow"
    },
    {
        "id": "id7",
        "timestamp": 12347,
        "name": "Golden Delicious",
        "color": "yellow"
    }
]


class TestSearch:

    @pytest.fixture(autouse=True)
    async def documents(self, typesense, collection_schema):
        try:
            created = await typesense.collections.create(collection_schema)
            await typesense.collections["fruits"].documents.create_many(
                testing_documents
            )
            yield
        finally:
            await typesense.collections[created["name"]].delete()

    async def test_search_general(self, typesense):
        collection: Collection[AppleType] = typesense.collections["fruits"]
        result = await collection.documents.search(
            q="apple", query_by=["name"]
        )
        assert len(result["hits"]) == 2

    async def test_search_filter(self, typesense):
        collection: Collection[AppleType] = typesense.collections["fruits"]
        result = await collection.documents.search(
            q="*", query_by=["name"], filter_by="color:red"
        )
        assert len(result["hits"]) == 3

    async def test_search_facet(self, typesense):
        collection: Collection[AppleType] = typesense.collections["fruits"]
        result = await collection.documents.search(
            q="*", query_by=["name"], facet_by="color"
        )
        assert len(result["facet_counts"]) == 1
        assert len(result["facet_counts"][0]["counts"]) == 3
        assert result["found"] == 7
