import httpx
import orjson
from typing import List, NamedTuple
from .config import Configuration


class Requester:

    encoder = orjson.dumps
    decoder = orjson.loads

    def __init__(self, config: Configuration, headers: dict | None = None):
        self.config = config
        if headers is None:
            headers = {}
        headers["X-TYPESENSE-API-KEY"] = self.config.api_key
        self.headers = headers

    async def get_node(self):
        return self.config.urls[0]

    async def request(self,
                       method: str,
                       endpoint: str,
                       *,
                       data=None,
                       params=None,
                       headers: dict | None =None):
        node = await self.get_node()
        url = f"{node}/{endpoint.strip('/')}"
        headers = (headers or {}) | self.headers

        if data is not None and not isinstance(data, bytes):
            headers["Content-Type"] = "application/json"
            data = self.encoder(data)

        http_client: httpx.AsyncClient
        async with httpx.AsyncClient() as http_client:
            response: httpx.Response = await http_client.request(
                method,
                url,
                content=data,
                headers=headers,
                params=params,
                timeout=2

            )
        return response

    async def get(self,
                  endpoint: str,
                  *,
                  params=None,
                  headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request(
            'GET', endpoint, params=params, headers=headers)
        response.raise_for_status()
        if as_json:
            return self.decoder(response.content)
        return response.content

    async def post(self,
                   endpoint,
                   *,
                   data=None,
                   params=None,
                   headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request(
            'POST', endpoint, params=params, data=data, headers=headers)
        response.raise_for_status()
        if as_json:
            return self.decoder(response.content)
        return response.content

    async def put(self,
                  endpoint,
                  *,
                  data=None,
                  params=None,
                  headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request(
            'PUT', endpoint, params=params, data=data, headers=headers)
        response.raise_for_status()
        if as_json:
            return self.decoder(response.content)
        return response.content

    async def patch(self,
                    endpoint,
                    *,
                    data=None,
                    params=None,
                    headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request(
            'PATCH', endpoint, params=params, data=data, headers=headers)
        response.raise_for_status()
        if as_json:
            return self.decoder(response.content)
        return response.content

    async def delete(self,
                     endpoint: str,
                     *,
                     params=None,
                     headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request(
            'DELETE', endpoint, params=params, headers=headers)
        response.raise_for_status()
        if as_json:
            return self.decoder(response.content)
        return response.content
