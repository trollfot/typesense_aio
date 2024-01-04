import ssl
from typing import List, NamedTuple, Literal


class Configuration(NamedTuple):
    urls: List[str]
    api_key: str
    timeout: float = 5.0
    retries: int = 3
    retry_interval: float = 1.0
    healthcheck_interval: float = 60.0
    verify: Literal[False] | str | ssl.SSLContext = False
