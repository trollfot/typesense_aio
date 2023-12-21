import pytest
from typesense_aio.nodes import Node, Nodes


def test_node_repr():
    node = Node('http://test.com:80/indexer')
    assert repr(node) == "<Node 'http://test.com:80/indexer' status=OK>"

    node.healthy = False
    assert repr(node) == "<Node 'http://test.com:80/indexer' status=KO>"


def test_node_equality():
    node = Node('http://test.com:80/indexer')
    assert node == 'http://test.com:80/indexer'
    assert node.healthy == True
    assert node.url.scheme == 'http'

    node2 = Node(node)
    assert node2 is node

    node3 = Node('http://test.com:80/indexer')
    assert node == node3

    node3.healthy = False  # Node health does play a big part in equality
    assert node != node3
    assert node is not node3


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
    nodes = Nodes(
        [
            'http://test.com:80/indexer',
            'http://example.com:12345/',
        ]
    )

    assert len(nodes) == 2
    assert set(nodes) == set((
        Node('http://test.com:80/indexer'),
        Node('http://example.com:12345/')
    ))


def test_nodes_quarantine():
    node1 = Node('http://test.com:80/indexer')
    node2 = Node('http://example.com:12345/')
    nodes = Nodes((node1, node2))

    assert len(nodes) == 2
    assert set(nodes) == set((node1, node2))

    nodes.quarantine(node1)
    assert len(nodes) == 1
    assert set(nodes) == set((node2,))
    assert node1.healthy == False

    nodes.quarantine(node2)
    assert len(nodes) == 0
    assert set(nodes) == set()
    assert node2.healthy == False

    nodes.restore(node1)
    assert len(nodes) == 1
    assert set(nodes) == set((node1,))
    assert node1.healthy == True
    assert node2.healthy == False


def test_nodes_quarantine_intruder():
    node1 = Node('http://test.com:80/indexer')
    node2 = Node('http://example.com:12345/')
    intruder = Node('http://unknown.com:567/endpoint')
    nodes = Nodes((node1, node2))

    assert len(nodes) == 2
    assert set(nodes) == set((
        Node('http://test.com:80/indexer'),
        Node('http://example.com:12345/')
    ))

    with pytest.raises(LookupError):
        nodes.quarantine(intruder)

    with pytest.raises(LookupError):
        nodes.restore(intruder)

    assert len(nodes) == 2
    assert set(nodes) == set((node1, node2))

    sneaky_node = Node('http://test.com:80/indexer')
    nodes.quarantine(node1)

    with pytest.raises(LookupError):
        nodes.restore(sneaky_node)
