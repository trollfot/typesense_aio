import pytest
import httpx
import hamcrest


class TestDebug:

    async def test_debug_access(self, typesense):
        debug_info = await typesense.debug.retrieve()
        assert debug_info == {
            'state': 1,
            'version': '0.25.1'
        }
