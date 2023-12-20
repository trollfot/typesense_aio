import httpx
import pytest
from unittest import mock


class TestAnalytics:

    async def test_analytics_lifecycle(self, typesense):
        created = await typesense.analytics.rules['my_rule'].upsert({
            "type": "popular_queries",
            "params": {
                "source": {
                    "collections": ["products"]
                },
                "destination": {
                    "collection": "product_queries"
                },
                "limit": 1000
            }
        })
        assert created == {
            'name': 'my_rule',
            'params': {
                'destination': {
                    'collection': 'product_queries'
                },
                'limit': 1000,
                'source': {
                    'collections': ['products']
                }
            },
            'type': 'popular_queries'
        }


        found = await typesense.analytics.rules.retrieve()
        assert found == {
            'rules': [{
                'name': 'my_rule',
                'params': {
                    'destination': {
                        'collection': 'product_queries'
                    },
                    'limit': 1000,
                    'source': {
                        'collections': ['products']
                    }
                },
                'type': 'popular_queries'
            }]
        }

        result = await typesense.analytics.rules['my_rule'].delete()
        assert result == {'name': 'my_rule'}
