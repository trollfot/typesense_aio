import httpx
import pytest
from unittest import mock


class TestDocuments:

    @pytest.fixture(autouse=True)
    async def collection(self, typesense, collection_schema):
        try:
            created = await typesense.collections.create(collection_schema)
            yield
        finally:
            await typesense.collections[created["name"]].delete()

    async def test_document_get_not_exists(self, typesense):
        doc = await typesense.collections["fruits"].documents["B"].retrieve()
        assert doc is None

    async def test_document_get(self, typesense):
        doc = {
            "id": "A",
            "name": "Red Delicious",
            "timestamp": 23452345,
            "color": "red",
        }
        collection = typesense.collections["fruits"]

        created = await collection.documents.create(doc)
        assert created == doc

        fetched = await collection.documents["A"].retrieve()
        assert fetched == doc

    async def test_document_delete(self, typesense):
        doc = {
            "id": "A",
            "name": "Red Delicious",
            "timestamp": 3253425,
            "color": "red",
        }

        created = await typesense.collections["fruits"].documents.create(doc)
        assert created == doc

        deleted = await typesense.collections["fruits"].documents["A"].delete()
        assert deleted == doc

    async def test_document_update(self, typesense):
        doc = {
            "id": "A",
            "name": "Red Delicious",
            "timestamp": 3253425,
            "color": "red",
        }

        created = await typesense.collections["fruits"].documents.create(doc)
        assert created == doc

        updated = (
            await typesense.collections["fruits"]
            .documents["A"]
            .update({"name": "Golden Delicious"})
        )
        assert updated == {**doc, "name": "Golden Delicious"}

    async def test_document_get_raises(self, typesense):
        document_obj = typesense.collections["fruits"].documents["doc_id"]

        with mock.patch.object(document_obj.requester, "request") as mockreq:
            mockreq.side_effect = ValueError("error")

            with pytest.raises(ValueError):
                await document_obj.retrieve()

        with mock.patch.object(document_obj.requester, "request") as mockreq:
            httpx_response_mock = mock.Mock()
            httpx_response_mock.status_code = 300
            mockreq.side_effect = httpx.HTTPStatusError(
                "msg", request=mock.Mock(), response=httpx_response_mock
            )

            with pytest.raises(httpx.HTTPStatusError):
                await document_obj.retrieve()
