import pytest


class TestAliases:

    async def test_alias_lifecycle(self, typesense):
        found = await typesense.aliases.retrieve()
        assert found == {
            "aliases": []
        }

        created = await typesense.aliases['companies'].upsert({
            'collection_name': 'companies_june11'
        })
        assert created == {
            'collection_name': 'companies_june11',
            'name': 'companies'
        }

        found = await typesense.aliases['companies'].retrieve()
        assert found == {
            'collection_name': 'companies_june11',
            'name': 'companies'
        }

        found = await typesense.aliases.retrieve()
        assert found == {
            "aliases": [{
                'collection_name': 'companies_june11',
                'name': 'companies'
            }]
        }

        result = await typesense.aliases['companies'].delete()
        assert result == {
            'collection_name': 'companies_june11',
            'name': 'companies'
        }

        found = await typesense.aliases.retrieve()
        assert found == {
            "aliases": []
        }
