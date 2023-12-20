import httpx
import orjson
from .config import Configuration
from .nodes import Nodes, Node
from .exc import resolve_exception, service_exceptions
from contextlib import asynccontextmanager
from the_retry import retry


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
        self.request_with_retry = retry(
            expected_exception=service_exceptions,
            attempts=config.retries,
            backoff=config.retry_interval
        )(self.request)

    def get_node(self) -> Node | None:
        if self.nodes:
            return next(iter(self.nodes))

    async def check_quarantined_node(self):
        responding = set()
        while self.quarantined:
            item = self.quarantined.pop()
            try:
                health = await self.request.get('/health')
                if health == {"ok": True}:
                    node.healthy = True
                    responding.add(node)
            except:
                pass

        for valid in responding:
            self.nodes.restore(valid)

    async def request(self,
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
        async with httpx.AsyncClient() as http_client:
            response: httpx.Response = await http_client.request(
                method,
                url,
                content=data,
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )
        if not 200 <= response.status_code < 300:
            error_message = response.content
            error = resolve_exception(response.status_code)
            self.nodes.quarantine(node)
            raise error(error_message)

        return response

    async def get(self,
                  endpoint: str,
                  *,
                  params=None,
                  headers: dict | None = None,
                  as_json: bool = True):
        response = await self.request_with_retry(
            'GET',
            endpoint,
            params=params,
            headers=headers
        )
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
        response = await self.request_with_retry(
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
        response = await self.request_with_retry(
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
        response = await self.request_with_retry(
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
        response = await self.request_with_retry(
            'DELETE',
            endpoint,
            params=params,
            headers=headers
        )
        if as_json:
            return self.decoder(response.content)
        return response.content
