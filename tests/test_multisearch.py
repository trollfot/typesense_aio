import pytest
from typing import TypedDict, List


class FruitOrVeggieType(TypedDict):
    id: str
    timestamp: int
    name: str
    color: str


testing_fruits: List[FruitOrVeggieType] = [
    {
        "id": "id1",
        "timestamp": 12341,
        "name": "Granny Smith",
        "color": "green"
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
    }
]

testing_veggies: List[FruitOrVeggieType] = [
    {
        "id": "id4",
        "timestamp": 12351,
        "name": "Bell Pepper",
        "color": "red"
    },
    {
        "id": "id5",
        "timestamp": 12352,
        "name": "Poblano Pepper",
        "color": "green"
    },
    {
        "id": "id6",
        "timestamp": 12353,
        "name": "Anaheim Pepper",
        "color": "green"
    }
]


class TestMultiSearch:

    @pytest.fixture(autouse=True)
    async def documents(self, typesense, collection_schema):
        try:
            fruits = await typesense.collections.create(collection_schema)
            veggies = await typesense.collections.create({
                **collection_schema, "name": "veggies"
            })
            await typesense.collections["fruits"].documents.create_many(
                testing_fruits
            )
            await typesense.collections["veggies"].documents.create_many(
                testing_veggies
            )
            yield
        finally:
            await typesense.collections[fruits["name"]].delete()
            await typesense.collections[veggies["name"]].delete()


    async def test_multi_search_no_params(self, typesense):
        response = await typesense.multi_search.perform({
            "searches": [
            {
                "collection": "fruits",
                "q": '*',
                "filter_by": 'color:=red'
            },
            {
                "collection": 'veggies',
                "q": "Bell",
                "query_by": "name"
            }
        ]})
        results = response['results']
        assert len(results) == 2
        assert results[0]['found'] == 2
        assert results[1]['found'] == 1

    async def test_multi_search_params(self, typesense):
        common_search_params =  {
            "query_by": "name",
            "filter_by": 'color:=red'
        }
        response = await typesense.multi_search.perform({
            "searches": [
                {
                    "collection": "fruits",
                    "q": 'Ambrosia'
                },
                {
                    "collection": 'veggies',
                    "q": "*"
                }
            ]
        }, params=common_search_params)
        results = response['results']
        assert len(results) == 2
        assert results[0]['found'] == 1
        assert results[1]['found'] == 1
