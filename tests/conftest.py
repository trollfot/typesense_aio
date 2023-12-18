import asyncio
import uuid
import socket
import pytest
import docker
from contextlib import closing
from typing import List
from docker.models.containers import Container
from typesense_aio.client import Client
from typesense_aio.config import Configuration
from typesense_aio.types import CollectionDict


TYPESENSE_DOCKER_IMAGE = "typesense/typesense:0.25.1"


def start_container(
        datadir,
        api_key: str,
        port: int,
        docker_base_url: str = "unix://var/run/docker.sock") -> Container:

    docker_client = docker.DockerClient(
        base_url=docker_base_url,
        version="auto"
    )

    docker_client.api.pull(TYPESENSE_DOCKER_IMAGE)

    container: Container = docker_client.containers.create(
        image=TYPESENSE_DOCKER_IMAGE,
        command=[
            "--api-key=" + api_key,
            "--data-dir=/data",
            "--enable-cors"
        ],
        name=f"test-typesense-{uuid.uuid4()}",
        detach=True,
        ports={8108: ('127.0.0.1', port)},
        volumes={
            str(datadir): {
                "bind": "/data", "mode": "rw"
            }
        },
    )
    container.start()
    return container


@pytest.fixture(scope="session")
def collection_schema() -> CollectionDict:
    return {
        "name": "fruits",
        "num_documents": 0,
        "fields": [
            {
                "name": "name",
                "type": "string",
            },
            {
                "name": "timestamp",
                "type": "int32",
            },
            {
                "name": "description",
                "type": "string",
                "optional": True,
            },
            {
                "name": "color",
                "type": "string",
                "facet": True,
            },
        ],
        "default_sorting_field": "timestamp",
    }


@pytest.fixture(scope="session")
def service_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def api_key() -> str:
    return "Rhsdhas2asasdasj2"


@pytest.fixture(scope="session")
def configuration(api_key, service_port):
    return Configuration(
        urls=[f"http://127.0.0.1:{service_port}"],
        api_key=api_key
    )


@pytest.fixture(scope="class")
async def typesense(configuration, api_key, service_port, tmpdir_factory):
    try:
        datadir = tmpdir_factory.mktemp("data")
        container = start_container(
            datadir, api_key=api_key, port=service_port)
        client = Client(configuration)
        await client.health.wait()
        yield client
    finally:
        container.kill()
        container.remove()
        container.client.close()


@pytest.fixture(scope="function", autouse=True)
async def collections(typesense):
    yield
    collections: List[dict] = await typesense.collections.retrieve()
    if collections:
        for collection in collections:
            await typesense.collections[collection["name"]].delete()
