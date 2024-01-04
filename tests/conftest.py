import uuid
import ssl
import socket
import pytest
import docker
import httpx
import os
from contextlib import closing
from docker.models.containers import Container
from typesense_aio.client import Client
from typesense_aio.config import Configuration
from typesense_aio.types import CollectionDict


TYPESENSE_DOCKER_IMAGE = "typesense/typesense:0.25.1"


SERVER_CERT = """-----BEGIN CERTIFICATE-----
MIIDDzCCAfegAwIBAgIUS6znUgPwm08Y856etV8MSs/rtQAwDQYJKoZIhvcNAQEL
BQAwFDESMBAGA1UEAwwJbG9jYWxob3N0MB4XDTI0MDEwMzE4NDMxMFoXDTI0MDIw
MjE4NDMxMFowFDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAtmmM9HmvSBIJU1edi2crWRCaMEHgzDe+w/cGwyaxFVqi
Af0nYIW/bUkNwcA6PM+qIdcWmPTOe0T2ObRBEuoQEpREQ9GVxSkjTR+q35C2vAt9
jYlkekreVIxWby8MFXX7QPxdKNxGfhaEec6ohbDA29ht9YbXsLlZQEs156uyTqu8
Y6OlOwJ5Do7KAE6C6H1jiV91lYtvZCEgpR7x9A/fHHm23VbYUJ0V0xDN7W193RFy
F3HXs0oVBEWmQcBndj+oXOtukptGWG9tcKwvp2WQlhJ165sPrCS4Zs5civgE0zjv
IeWeL9r1sLMV3MamFXaL3Ng0SrL5ClACoiPdWXJpZQIDAQABo1kwVzAUBgNVHREE
DTALgglsb2NhbGhvc3QwCwYDVR0PBAQDAgeAMBMGA1UdJQQMMAoGCCsGAQUFBwMB
MB0GA1UdDgQWBBSDOxT+x7m0Vs3NlRcO6MV9JAm++DANBgkqhkiG9w0BAQsFAAOC
AQEAdBC0jpmneLqBgcVkK6c+44+3+L1ym+qjoBd1VEcaJCRHu4+Zgi4ATMZ6M5Pg
s+pkfvB2NLLYbPPZD+CMRnOemMA4h7LIhUuVPuwJ6Jnc8wf9qipLRlDdX1T+Outl
ECV5IddpxEe8qhfaLC1CoJLIPGRaDc1mORWs7rwQfSSbXRx5kmjU26n2fWtL4X+I
tY37Vz7IevNPoeiL/BTSp0r0xxLiOQ7lsAR0ThhZuqqlV3lK98I/nPSJot0g97Wo
nrM7sLLbTmlUYRiv/RZa09v9R1bbQ3+0061uo1MHuiHKy0c1d4o3+C9FC+rafBCm
2B6iL0VLCZmeKdoIjHb3cosolA==
-----END CERTIFICATE-----
"""

SERVER_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2aYz0ea9IEglT
V52LZytZEJowQeDMN77D9wbDJrEVWqIB/Sdghb9tSQ3BwDo8z6oh1xaY9M57RPY5
tEES6hASlERD0ZXFKSNNH6rfkLa8C32NiWR6St5UjFZvLwwVdftA/F0o3EZ+FoR5
zqiFsMDb2G31htewuVlASzXnq7JOq7xjo6U7AnkOjsoAToLofWOJX3WVi29kISCl
HvH0D98cebbdVthQnRXTEM3tbX3dEXIXcdezShUERaZBwGd2P6hc626Sm0ZYb21w
rC+nZZCWEnXrmw+sJLhmzlyK+ATTOO8h5Z4v2vWwsxXcxqYVdovc2DRKsvkKUAKi
I91ZcmllAgMBAAECggEAETbdTT4Fj2LaW/HfBYaXNejF8EtrREJ3f4Var0SBvi7n
LpJeKrL8iXr1MCVsqYv8dYSXlpg1uzbbGL98y6TonuQ8m/zVqj1TXkYgiUgeIplg
ACEo6QyTNj3nM0dol8biTvPx87bz9Ra5akhZKYKwdJ7UY7EVvlEDjfh7DhGrOla8
UmbQS52/3XFbwqcyQVAJHBcSbLwcK+A/KxTxOWTA5AfA2TiIq/FXv/mG75pXWAXK
j60p0E/4j11F7cMRHTThkoEhJDStnNySU/UyyugXC6vtTGTF1ZMJ5sOr8n9fXDap
eKF8/HipIOYpn12q/knF+chWL7IwnSiDo6CoCnd2+QKBgQDjKjUOk4AAp2HoMtcQ
Rs9LePBC4cS6g16BF74LCqcMB7BHVPtFlwpHF4NzoEspdGxQfpGmLh+IOgz8ugih
LptsfRBWtTrNSBHYzRbBdI3DrubK/fUJxh0frxfL7dZj8gSunieYTl0bakTFPQ72
YppATE9mb06rQkqmHFC8PhClOQKBgQDNkRhMZlX8IslIvo6PCVr2C4WZ1rhWRt4g
YcxifALP7HRhPjqxCQZrDBb8O3gIyn2OkDSFHNNXjl1oA+pHLzB4IBvYXZ39N45n
t4tCIeCGmRXgP7H0incWVy8EgThGnDkjlGoltoqLqJyB9k7lyic8LLxBfrMCLK5q
T5Fu22OxjQKBgCD06qWmuJdfsVCir5jo7QIiFZleb9AvZvKLo0Ku1PVl2ClBJwM9
mnwd6TBJPR5SibRT6IWXg3OcGG5B/yaDQIFI06oAuPs3TX+KoZaHdlnBcjJZDcfR
OkBygp1PcB8n6Y372/q4w8FKdZe3+Ae+3modqBdQZrVp9LKMwRnOV1PhAoGBAKf2
IdBq3V7CXYyehoTAtB3NlD/6fWuhQ+VZg1IE2ZdiMEU0P2hfY2sb2bwGKzGjoatW
kFMjFlu36wIOEOJQ4F2Gfrnu5CP9vNFp2tMSMw5HDuTHpnOUn3EVk0ku+/hVtSop
HgHqgJFUF2zo/9Ypsp0sQDWTfFgOggRDNyVJBNARAoGAfyrK9JF9Ft1hr1crosHa
eB3kL8zfIZMpuntOj3Avr8LJdxko9Q6FHlwLKTNi6JG4XBTje5stoUlJkM9EBWjJ
fLr5GlzhPnVUSfIlcNdfd4GvFER0oeaQU2+7pfwBEzSBnrL5A1G0bOzaZsHLohUD
v4dLPP9VA2ddD2WTprpg5yM=
-----END PRIVATE KEY-----"""


@pytest.fixture(scope="session")
def server_cert(tmpdir_factory):
    certs = tmpdir_factory.mktemp("certs")
    certpath = certs.join("server.crt")
    keypath = certs.join("server.key")
    certpath.write(SERVER_CERT)
    keypath.write(SERVER_KEY)
    previous = os.environ.get("SSL_CERT_FILE")
    os.environ["SSL_CERT_FILE"] = str(certpath)
    yield certpath, keypath
    if previous:
        os.environ["SSL_CERT_FILE"] = previous


@pytest.fixture(scope="session")
def httpserver_ssl_context(server_cert):
    cert, key = server_cert
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(cert, keyfile=key)
    return server_context


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


@pytest.fixture(scope="session")
async def typesense(configuration, api_key, service_port, tmpdir_factory):
    try:
        datadir = tmpdir_factory.mktemp("data")
        container = start_container(
            datadir, api_key=api_key, port=service_port)
        client = Client(configuration)

        async with httpx.AsyncClient() as http_client:
            ok = False
            while not ok:
                response = await http_client.request(
                    'GET',
                    configuration.urls[0] + '/health',
                    timeout=5
                )
                if response.status_code == 200:
                    break
                elif response.status_code == 503:
                    continue
                else:
                    response.raise_for_status()
        yield client
    finally:
        container.kill()
        container.remove()
        container.client.close()
