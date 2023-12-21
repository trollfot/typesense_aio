import httpx
import pytest
import hamcrest
from unittest import mock


class TestCollections:

    @pytest.fixture(scope="function", autouse=True)
    async def collections(self, typesense):
        yield
        collections: List[dict] = await typesense.collections.retrieve()
        if collections:
            for collection in collections:
                await typesense.collections[collection["name"]].delete()

    async def test_collection_get_not_exists(self, typesense):
        collection = await typesense.collections["fruits"].retrieve()
        assert collection is None

    async def test_collection_get(self, typesense, collection_schema):
        created_col = await typesense.collections.create(collection_schema)
        assert "name" in created_col
        assert "fields" in created_col

        collection = await typesense.collections["fruits"].retrieve()
        assert collection["name"] == "fruits"

    async def test_collections_get_no_collections(self, typesense):
        collections = await typesense.collections.retrieve()
        assert len(collections) == 0

    async def test_collection_get_raises(self, typesense):
        collection_obj = typesense.collections["fruits"]

        with mock.patch.object(collection_obj.requester, "request") as mockreq:
            mockreq.side_effect = ValueError("error")

            with pytest.raises(ValueError):
                await collection_obj.retrieve()

        with mock.patch.object(collection_obj.requester, "request") as mockreq:
            httpx_response_mock = mock.Mock()
            httpx_response_mock.status_code = 300
            mockreq.side_effect = httpx.HTTPStatusError(
                "msg", request=mock.Mock(), response=httpx_response_mock
            )

            with pytest.raises(httpx.HTTPStatusError):
                await collection_obj.retrieve()

    async def test_collections_create(self, typesense, collection_schema):
        created_col = await typesense.collections.create(collection_schema)
        hamcrest.assert_that(created_col, hamcrest.has_entries({
            'created_at': hamcrest.instance_of(int),
            'default_sorting_field': 'timestamp',
            'enable_nested_fields': False,
            'fields': [
                {
                    'facet': False,
                    'index': True,
                    'infix': False,
                    'locale': '',
                    'name': 'name',
                    'optional': False,
                    'sort': False,
                    'type': 'string'
                }, {
                    'facet': False,
                    'index': True,
                    'infix': False,
                    'locale': '',
                    'name': 'timestamp',
                    'optional': False,
                    'sort': True,
                    'type': 'int32'
                }, {
                    'facet': False,
                    'index': True,
                    'infix': False,
                    'locale': '',
                    'name': 'description',
                    'optional': True,
                    'sort': False,
                    'type': 'string'
                }, {
                    'facet': True,
                    'index': True,
                    'infix': False,
                    'locale': '',
                    'name': 'color',
                    'optional': False,
                    'sort': False,
                    'type': 'string'
                }
            ],
            'name': 'fruits',
            'num_documents': 0,
            'symbols_to_index': [],
            'token_separators': []
        }))

    async def test_collections_get(self, typesense, collection_schema):
        created_col = await typesense.collections.create(collection_schema)
        assert "name" in created_col
        assert "fields" in created_col

        await typesense.collections.create(
            {**collection_schema, "name": "fruits2"}
        )

        await typesense.collections.create(
            {**collection_schema, "name": "fruits3"}
        )

        collections = await typesense.collections.retrieve()
        assert len(collections) == 3
