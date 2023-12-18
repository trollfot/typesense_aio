from urllib.parse import urlparse, ParseResult


class Node(str):

    url: ParseResult
    healthy: bool = True

    def __new__(cls, value: str | Node):
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
        return inst
