from time import time
from urllib.parse import urlparse, ParseResult
from collections.abc import Hashable, MutableSet
from typing import Iterable, Union


class Node(str):

    url: ParseResult
    healthy: bool = True

    def __eq__(self, other: Union['Node', str]):
        if isinstance(other, Node):
            return (self.url == other.url and self.healthy == other.healthy)

        if isinstance(other, str):
            return super().__eq__(other)

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

        url = urlparse(value)
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


class Nodes:

    def __init__(self, iterable: Iterable[Node | str]):
        self.quarantined = set()
        self.pool = set((Node(v) for v in iterable))

    def __iter__(self):
        return iter(self.pool)

    def __len__(self):
        return len(self.pool)

    def quarantine(self, node: Node):
        if node in self.pool:
            node.healthy = False
            self.pool.discard(node)
            self.quarantined.add(node)
        elif node in self.quarantined:
            # already quarantined.
            pass
        else:
            raise LookupError('Unknown node.')

    def restore(self, node: Node):
        if node in self.quarantined:
            node.healthy = True
            self.quarantined.discard(node)
            self.pool.add(node)
        elif node in self.pool:
            # already quarantined.
            pass
        else:
            raise LookupError('Unknown node.')
