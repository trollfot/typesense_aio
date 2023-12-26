class TestConfig:

    async def test_log_slow_request(self, typesense):
        result = await typesense.log_slow_request()
        assert result == {'success': True}

        result = await typesense.log_slow_request(-1)
        assert result == {'success': True}
