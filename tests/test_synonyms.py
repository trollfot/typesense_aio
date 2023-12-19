import pytest
import httpx
from typesense_aio.client import Client
from typesense_aio.collections import Collection
from typing import List, TypedDict


class ClothingType(TypedDict):
    id: str
    timestamp: int
    name: str


clothing_schema = {
        "name": "clothing",
        "num_documents": 0,
        "fields": [
            {
                "name": "name",
                "type": "string",
            },
            {
                "name": "timestamp",
                "type": "int32",
            }
        ],
        "default_sorting_field": "timestamp",
    }


testing_documents: List[ClothingType] = [
    {
        "id": "id1",
        "timestamp": 12341,
        "name": "Jacket",
    },
    {
        "id": "id2",
        "timestamp": 12342,
        "name": "Shirt",
    },
    {
        "id": "id3",
        "timestamp": 12343,
        "name": "Skirt",
    }
]


class TestSynonyms:

    @pytest.fixture(autouse=True)
    async def documents(self, typesense, collection_schema):
        try:
            created = await typesense.collections.create(clothing_schema)
            await typesense.collections["clothing"].documents.create_many(
                testing_documents
            )
            yield
        finally:
            await typesense.collections["clothing"].delete()

    async def test_create_synonyms(self, typesense):
        collection = typesense.collections['clothing']
        synonym = await collection.synonyms['coat-synonyms'].upsert({
            "synonyms": ["blazer", "coat", "jacket"]
        })
        assert synonym == {
            'id': 'coat-synonyms',
            'synonyms': ['blazer', 'coat', 'jacket']
        }

    async def test_synonyms_get(self, typesense):
        collection = typesense.collections['clothing']
        await collection.synonyms['coat-synonyms'].upsert({
            "synonyms": ["blazer", "coat", "jacket"]
        })
        synonym = await collection.synonyms['coat-synonyms'].retrieve()
        assert synonym == {
            'id': 'coat-synonyms',
            'root': '',
            'synonyms': ['blazer', 'coat', 'jacket']
        }

    async def test_synonyms_delete(self, typesense):
        collection = typesense.collections['clothing']
        await collection.synonyms['coat-synonyms'].upsert({
            "synonyms": ["blazer", "coat", "jacket"]
        })
        response = await collection.synonyms['coat-synonyms'].delete()
        assert response == {'id': 'coat-synonyms'}
        synonyms = await collection.synonyms.retrieve()
        assert synonyms == {'synonyms': []}

    async def test_synonyms_list(self, typesense):
        collection = typesense.collections['clothing']

        await collection.synonyms['coat-synonyms'].upsert({
            "synonyms": ["blazer", "coat", "jacket"]
        })

        synonyms = await collection.synonyms.retrieve()
        assert synonyms == {
            'synonyms': [
                {
                    'id': 'coat-synonyms',
                    'root': '',
                    'synonyms': ['blazer', 'coat', 'jacket']
                }
            ]
        }
