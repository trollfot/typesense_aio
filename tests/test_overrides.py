import pytest


class TestOverrides:

    @pytest.fixture(autouse=True)
    async def collection(self, typesense, collection_schema):
        try:
            created = await typesense.collections.create(collection_schema)
            yield
        finally:
            await typesense.collections[created["name"]].delete()

    async def test_override_lifecycle(self, typesense):
        collection = typesense.collections["fruits"]

        found = await collection.overrides.retrieve()
        assert found == {'overrides': []}

        created = await collection.overrides['customize-apple'].upsert({
            "rule": {
                "query": "apple",
                "match": "exact"
            },
            "includes": [
                {"id": "422", "position": 1},
                {"id": "54", "position": 2}
            ],
            "excludes": [
                {"id": "287"}
            ]
        })
        assert created == {
            'excludes': [{'id': '287'}],
            'id': 'customize-apple',
            'includes': [
                {'id': '422', 'position': 1},
                {'id': '54', 'position': 2}
            ],
            'rule': {'match': 'exact', 'query': 'apple'}
        }

        found = await collection.overrides['customize-apple'].retrieve()
        assert found == {
            'excludes': [{'id': '287'}],
            'filter_curated_hits': False,
            'id': 'customize-apple',
            'includes': [
                {'id': '422', 'position': 1},
                {'id': '54', 'position': 2}
            ],
            'remove_matched_tokens': False,
            'rule': {'match': 'exact', 'query': 'apple'},
            'stop_processing': True
        }

        result = await collection.overrides['customize-apple'].delete()
        assert result == {
            'id': 'customize-apple'
        }

        found = await collection.overrides.retrieve()
        assert found == {'overrides': []}
