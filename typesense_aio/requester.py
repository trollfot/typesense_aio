import asyncio
import httpx
import orjson
from the_retry import retry
from .types import BaseRequester
from .config import Configuration
from .nodes import Node, SingleNode, NodeList
from .exc import (
    resolve_exception,
    service_exceptions,
    ObjectNotFound,
)


class Requester(BaseRequester):

    encoder = orjson.dumps
    decoder = orjson.loads

    def __init__(self, config: Configuration, headers: dict | None = None):
        if headers is None:
            headers = {}
        headers["X-TYPESENSE-API-KEY"] = config.api_key
        self.headers = headers

        node_policy = SingleNode if len(config.urls) == 1 else NodeList
        self.nodes = node_policy(config.urls, config.healthcheck_interval)

        self.request = retry(
            expected_exception=service_exceptions,
            attempts=config.retries,
            backoff=config.retry_interval
        )(self._request)
        self.timeout: float = config.timeout

    def handle_faulty_node(self, node: Node) -> None:
        self.nodes.quarantine(node)

    async def _request(self,
                      method: str,
                      endpoint: str,
                      *,
                      data=None,
                      params=None,
                      headers: dict | None = None):

        node = self.nodes.get()
        if node is None:
            raise LookupError('No valid nodes.')

        url = f"{node}/{endpoint.strip('/')}"
        headers = (headers or {}) | self.headers

        if data is not None and not isinstance(data, bytes):
            headers["Content-Type"] = "application/json"
            data = self.encoder(data)

        http_client: httpx.AsyncClient
        try:
            async with httpx.AsyncClient() as http_client:
                response: httpx.Response = await http_client.request(
                    method,
                    url,
                    content=data,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
        except httpx.RequestError:
            self.handle_faulty_node(node)
            raise
        else:
            if not 200 <= response.status_code < 300:
                error_message = response.content
                error = resolve_exception(response.status_code)
                if error in service_exceptions:
                    self.handle_faulty_node(node)
                raise error(error_message)
        return response

    async def get(self,
                  endpoint: str,
                  *,
                  params=None,
                  headers: dict | None = None,
                  as_json: bool = True):
        try:
            response = await self.request(
                'GET',
                endpoint,
                params=params,
                headers=headers
            )
        except ObjectNotFound:
            return None
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
            'POST',
            endpoint,
            params=params,
            data=data,
            headers=headers
        )
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
            'PUT',
            endpoint,
            params=params,
            data=data,
            headers=headers
        )
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
            'PATCH',
            endpoint,
            params=params,
            data=data,
            headers=headers
        )
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
            'DELETE',
            endpoint,
            params=params,
            headers=headers
        )
        if as_json:
            return self.decoder(response.content)
        return response.content
