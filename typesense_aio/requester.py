import asyncio
import httpx
import orjson
from the_retry import retry
from .config import Configuration
from .nodes import Nodes, Node
from .exc import (
    resolve_exception,
    service_exceptions,
    ObjectNotFound,
)


class Requester:

    encoder = orjson.dumps
    decoder = orjson.loads

    def __init__(self, config: Configuration, headers: dict | None = None):
        self.config = config
        if headers is None:
            headers = {}
        headers["X-TYPESENSE-API-KEY"] = self.config.api_key
        self.headers = headers
        self.nodes = Nodes(config.urls)
        self.request = retry(
            expected_exception=service_exceptions,
            attempts=config.retries,
            backoff=config.retry_interval
        )(self._request)

    def get_node(self) -> Node | None:
        if self.nodes:
            return next(iter(self.nodes))

    async def check_quarantined_node(self, node: Node):

        if node.healthy:
            return node

        http_client: httpx.AsyncClient
        async with httpx.AsyncClient() as http_client:
            response: httpx.Response = await http_client.request(
                'GET',
                f'{node}/health',
                timeout=self.config.timeout
            )
        try:
            response.raise_for_status()
        except httpx.HTTPError:
            return
        health = self.decoder(response.content)
        if health == {"ok": True}:
            return node
        return

    async def check_quarantined_nodes(self):
        tasks = [
            self.check_quarantined_node(node)
            for node in self.nodes.quarantined
        ]
        valid_nodes = await asyncio.gather(*tasks)
        for node in valid_nodes:
            if node is not None:
                self.nodes.restore(node)

    async def quarantine_guard(self):
        while True:
            if self.nodes.quarantined:
                await self.check_quarantined_nodes()
            await asyncio.sleep(self.config.healthcheck_interval)

    async def _request(self,
                      method: str,
                      endpoint: str,
                      *,
                      data=None,
                      params=None,
                      headers: dict | None = None):

        node = self.get_node()
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
                    timeout=self.config.timeout
                )
        except httpx.RequestError:
            self.nodes.quarantine(node)
            raise
        else:
            if not 200 <= response.status_code < 300:
                error_message = response.content
                error = resolve_exception(response.status_code)
                if error in service_exceptions:
                    self.nodes.quarantine(node)
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
