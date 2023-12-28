import asyncio
import httpx
from time import time
from urllib.parse import urlparse, ParseResult
from typing import Iterable, Union, MutableSet, Dict
from .types import NodePolicy
from .config import Configuration


class Node(str):

    url: ParseResult
    healthy: bool = True

    def __eq__(self, other: Union['Node', str]):
        if isinstance(other, Node):
            return (self.url == other.url and self.healthy == other.healthy)

        if isinstance(other, str):
            url = urlparse(other.rstrip('/'))
            return self.url == url

        raise NotImplementedError(
            f'Cannot compare a `Node` and {other.__class__!r}.')

    def __ne__(self, other: Union['Node', str]):
        return not self.__eq__(other)

    def __bool__(self):
        return self.healthy

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        url = super().__repr__()
        return f'<Node {url} status={self.healthy and "OK" or "KO"}>'

    def __new__(cls, value: Union[str, 'Node']):
        # idempotency
        if isinstance(value, Node):
            return value

        url = urlparse(value.rstrip('/'))
        if not url.hostname:
            raise ValueError('Node URL does not contain the host name.')

        if not url.port:
            raise ValueError('Node URL does not contain the port.')

        if not url.scheme:
            raise ValueError('Node URL does not contain the protocol.')

        inst = super().__new__(
            cls, f'{url.scheme}://{url.hostname}:{url.port}{url.path}')
        inst.url = url
        inst.healthy = True
        return inst


class SingleNode(NodePolicy):

    def __init__(self, urls, healthcheck_interval: float = 60.0):
        self.node: Node = Node(urls[0])

    def get(self) -> Node:
        return self.node


class NodeList(NodePolicy):

    def __init__(self, urls, healthcheck_interval: float = 60.0):
        self.quarantined: MutableSet[Node] = set()
        self.sane: MutableSet[Node] = set([Node(url) for url in urls])
        self.timers: Dict[Node, asyncio.Task] = {}
        self.check_interval: float = healthcheck_interval

    def get(self):
        if self.sane:
            return next(iter(self.sane))

    async def check_health(self, node) -> bool:
        url = f'{node}/health'
        try:
            async with httpx.AsyncClient() as http_client:
                response: httpx.Response = await http_client.request(
                    'GET', url, timeout=3.0
                )
        except httpx.RequestError:
            return False
        else:
            if response.status_code == 200:
                if response.json() == {"ok": True}:
                    if node.healthy is False:
                        return True
        return False

    async def health_task(self, node: Node, timer: float) -> None:
        await asyncio.sleep(timer)
        is_healthy: bool = await self.check_health(node)
        if is_healthy:
            self.restore(node)
            return True
        else:
            del self.timers[node]
            self.timers[node]: asyncio.Task = asyncio.ensure_future(
                self.health_task(node, self.check_interval)
            )
            return False

    def quarantine(self, node: Node) -> None:
        if node in self.sane:
            node.healthy = False
            self.sane.discard(node)
            self.quarantined.add(node)
        elif node in self.quarantined:
            # We can re-quarantine a node.
            # It resets the timer task.
            pass
        else:
            raise LookupError('Unknown node.')

        if node in self.timers:
            self.timers[node].cancel()
            del self.timers[node]

        self.timers[node]: asyncio.Task = asyncio.ensure_future(
            self.health_task(node, self.check_interval)
        )

    def restore(self, node: Node) -> None:
        if node not in self.quarantined:
            raise LookupError('Unknown node.')

        if node in self.timers:
            self.timers[node].cancel()
            del self.timers[node]

        node.healthy = True
        self.quarantined.discard(node)
        self.sane.add(node)
