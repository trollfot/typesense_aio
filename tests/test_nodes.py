import pytest
import httpx
import asyncio
import ssl
from typesense_aio.nodes import Node, NodeList
from typesense_aio.requester import Requester
from typesense_aio.config import Configuration


bad_response = httpx.Response(500)
good_response = httpx.Response(
    200,
    content=b'{"ok": true}',
    headers={'Content-Type': "application/json"}
)


def test_node_repr():
    node1 = Node('http://test.com:80/indexer')
    assert repr(node1) == "<Node 'http://test.com:80/indexer'>"

    node2 = Node('http://test.com:80/indexer///')
    assert repr(node2) == "<Node 'http://test.com:80/indexer'>"


def test_node_equality():
    node = Node('http://test.com:80/indexer')
    assert node == 'http://test.com:80/indexer'

    node2 = Node(node)
    assert node2 is node

    node3 = Node('http://test.com:80/indexer')
    assert node == node3
    assert node is not node3

    node4 = Node('http://test.com:80/indexer///')
    assert node == node4
    assert node is not node4


def test_node_wrong_url():
    with pytest.raises(ValueError) as exc:
        Node('test.com/indexer')

    assert str(exc.value) == 'Node URL does not contain the host name.'

    with pytest.raises(ValueError) as exc:
        Node('http://test.com/indexer')

    assert str(exc.value) == 'Node URL does not contain the port.'

    with pytest.raises(ValueError) as exc:
        Node('//test.com:80/indexer')

    assert str(exc.value) == 'Node URL does not contain the protocol.'


def test_nodes():
    nodes = NodeList(
        [
            'http://test.com:80/indexer',
            'http://example.com:12345/',
        ]
    )

    assert len(nodes.sane) == 2
    assert set(nodes.sane) == set((
        Node('http://test.com:80/indexer'),
        Node('http://example.com:12345/')
    ))


def test_nodes_quarantine():
    node1 = Node('http://test.com:80/indexer')
    node2 = Node('http://example.com:12345/')
    nodes = NodeList((node1, node2))

    assert len(nodes.sane) == 2
    assert nodes.sane == set((node1, node2))

    nodes.quarantine(node1)
    assert len(nodes.sane) == 1
    assert nodes.sane == set((node2,))

    nodes.quarantine(node2)
    assert len(nodes.sane) == 0
    assert nodes.sane == set()

    nodes.restore(node1)
    assert len(nodes.sane) == 1
    assert nodes.sane == set((node1,))


def test_nodes_quarantine_equal():
    node1 = Node('http://test.com:80/indexer')
    node2 = Node('http://example.com:12345/')
    intruder = Node('http://unknown.com:567/endpoint')
    nodes = NodeList((node1, node2))

    assert len(nodes.sane) == 2
    assert nodes.sane == set((
        Node('http://test.com:80/indexer'),
        Node('http://example.com:12345/')
    ))

    with pytest.raises(LookupError):
        nodes.quarantine(intruder)

    with pytest.raises(LookupError):
        nodes.restore(intruder)

    assert len(nodes.sane) == 2
    assert nodes.sane == set((node1, node2))

    equal_node = Node('http://test.com:80/indexer')
    nodes.quarantine(node1)

    assert len(nodes.sane) == 1


async def test_requester_bad_nodes_quarantine(api_key, respx_mock):

    respx_mock.get("http://example.com:12345/health").mock(
        return_value=bad_response
    )
    respx_mock.get("http://test.com:80/indexer/health").mock(
        return_value=bad_response
    )

    config = Configuration(
        urls=[
            "http://test.com:80/indexer",
            "http://example.com:12345/",
        ],
        api_key=api_key,
        timeout=0.5
    )
    requester = Requester(config)
    assert len(requester.nodes.sane) == 2
    assert requester.nodes.get() in (
        "http://test.com:80/indexer",
        "http://example.com:12345"
    )

    # all nodes are bad.
    with pytest.raises(LookupError):
        await requester.get('/health')

    assert requester.nodes.get() is None
    assert len(requester.nodes.quarantined) == 2


@pytest.mark.async_timeout(10)
async def test_requester_quarantine_task(api_key, respx_mock):

    respx_mock.get("http://example.com:12345/health").mock(
        return_value=bad_response
    )
    respx_mock.get("http://test.com:80/indexer/health").mock(
        return_value=bad_response
    )

    config = Configuration(
        urls=[
            "http://test.com:80/indexer",
            "http://example.com:12345/",
        ],
        api_key=api_key,
        timeout=0.5,
        healthcheck_interval=1
    )
    requester = Requester(config)

    # all nodes are bad.
    with pytest.raises(LookupError):
        await requester.get('/health')

    assert len(requester.nodes.quarantined) == 2

    respx_mock.get("http://example.com:12345/health").mock(
        return_value=good_response
    )
    await asyncio.sleep(2)
    assert len(requester.nodes.quarantined) == 1
    assert len(requester.nodes.timers) == 1


async def test_requester_verify_https(api_key, httpserver, server_cert):
    cert, key = server_cert
    sslcontext = ssl.SSLContext()
    sslcontext.load_verify_locations(cafile=cert)
    sslcontext.verify_mode = ssl.CERT_REQUIRED

    node = Node(httpserver.url_for('/'), verify=sslcontext)
    config = Configuration(
        urls=[node],
        api_key=api_key,
        timeout=0.5,
        healthcheck_interval=1
    )
    requester = Requester(config)
    httpserver.expect_request('/health', method="GET").respond_with_json(
        {"ok": True}
    )
    await requester.get('/health')


async def test_requester_unverified_https(api_key, httpserver):
    sslcontext = ssl.SSLContext()
    sslcontext.verify_mode = ssl.CERT_REQUIRED

    node = Node(httpserver.url_for('/'), verify=sslcontext)
    config = Configuration(
        urls=[node],
        api_key=api_key,
        timeout=0.5,
        healthcheck_interval=1
    )
    requester = Requester(config)
    httpserver.expect_request('/health', method="GET").respond_with_json(
        {"ok": True}
    )
    with pytest.raises(ssl.SSLCertVerificationError):
        await requester.get('/health')
