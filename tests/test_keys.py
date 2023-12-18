import pytest
import httpx
import hamcrest
from typesense_aio.types import CollectionDict


class TestKeys:

    async def test_key_get_not_exists(self, typesense):
        with pytest.raises(httpx.HTTPStatusError) as status_error:
            await typesense.keys[1].retrieve()

    async def test_keys_get_all_empty(self, typesense):
        all_keys = await typesense.keys.retrieve()
        assert all_keys == {
            'keys': []
        }

    async def test_keys_create_retrieve_delete(self, typesense):
        response = await typesense.keys.create({
            "description": "Search-only companies key.",
            "actions": ["documents:search"],
            "collections": ["companies"]
        })

        hamcrest.assert_that(response, hamcrest.has_entries({
            "actions": ["documents:search"],
            "collections":["companies"],
            "description":"Search-only companies key.",
            "expires_at": 64723363199,
            "id": 0,
            "value": hamcrest.instance_of(str)
        }))

        key = await typesense.keys[0].retrieve()
        hamcrest.assert_that(key, hamcrest.has_entries({
            'actions': ['documents:search'],
            'collections': ['companies'],
            'description': 'Search-only companies key.',
            'expires_at': 64723363199,
            'id': 0,
            'value_prefix': hamcrest.instance_of(str)
        }))

        await typesense.keys[0].delete()
        all_keys = await typesense.keys.retrieve()
        assert all_keys == {
            'keys': []
        }
