class TestStats:

    async def test_stats(self, typesense):
        result = await typesense.get_stats()
        assert result == {
            'delete_latency_ms': 0,
            'delete_requests_per_second': 0,
            'import_latency_ms': 0,
            'import_requests_per_second': 0,
            'latency_ms': {},
            'overloaded_requests_per_second': 0,
            'pending_write_batches': 0,
            'requests_per_second': {},
            'search_latency_ms': 0,
            'search_requests_per_second': 0,
            'total_requests_per_second': 0.0,
            'write_latency_ms': 0,
            'write_requests_per_second': 0,
        }
