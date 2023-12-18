import hmac
import base64
import hashlib


class Key:

    def __init__(self, requester, key_id):
        self.key_id = key_id
        self.requester = requester
        self.endpoint = f"/keys/{key_id}"

    async def retrieve(self):
        return await self.requester.get(self.endpoint)

    async def delete(self):
        return await self.requester.delete(self.endpoint)


class Keys:

    def __init__(self, requester):
        self.requester = requester
        self.keys = {}
        self.endpoint = '/keys'

    def __getitem__(self, key_id):
        if key_id not in self.keys:
            self.keys[key_id] = Key(self.requester, key_id)
        return self.keys.get(key_id)

    async def create(self, schema):
        return await self.requester.post(self.endpoint, data=schema)

    def generate_scoped_search_key(self, search_key, parameters):
        # Note: only a key generated with the `documents:search` action will be accepted by the server
        params_str = json.dumps(parameters)
        digest = base64.b64encode(
            hmac.new(
                search_key.encode('utf-8'),
                params_str.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
        )
        key_prefix = search_key[0:4]
        raw_scoped_key = f"{digest.decode('utf-8')}{key_prefix}{params_str}"
        return base64.b64encode(raw_scoped_key.encode('utf-8'))

    async def retrieve(self):
        return await self.requester.get(self.endpoint)
