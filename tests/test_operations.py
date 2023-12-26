import pytest


class TestOperations:

    async def test_operation_vote(self, typesense):
        result = await typesense.operations.perform('vote')
        assert result == {'success': False}

    async def test_operation_compact(self, typesense):
        result = await typesense.operations.perform('db/compact')
        assert result == {'success': True}
