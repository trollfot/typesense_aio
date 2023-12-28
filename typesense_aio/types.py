import typing as t
from abc import ABC, abstractmethod


JSON: t.TypeAlias = (
    dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
)


JSONEncoder = t.Callable[[JSON], t.AnyStr]
JSONDecoder = t.Callable[[t.AnyStr], JSON]


T = t.TypeVar("T")


class SchemaFieldDict(t.TypedDict):
    name: str
    type: t.Literal["string"] | t.Literal["string[]"] | t.Literal["int32"]
    facet: t.Optional[bool]
    optional: t.Optional[bool]


class CollectionDict(t.TypedDict):
    name: str
    num_documents: int
    fields: t.List[SchemaFieldDict]
    default_sorting_field: str


class SearchResponseHit(t.Protocol[T]):

    @t.overload
    def __getitem__(self, item: t.Literal["highlights"]) -> list[dict]:
        pass

    @t.overload
    def __getitem__(self, item: t.Literal["document"]) -> T:
        pass

    def __getitem__(self, item):
        pass


class SearchResponseFacetCountItem(t.TypedDict):
    counts: list[dict]
    field_name: str
    stats: list


class SearchResponse(t.Protocol[T]):

    @t.overload
    def __getitem__(
        self, item: t.Literal["facet_counts"]
    ) -> list[SearchResponseFacetCountItem]:
        pass

    @t.overload
    def __getitem__(self, item: t.Literal["took_ms"]) -> int:
        pass

    @t.overload
    def __getitem__(self, item: t.Literal["found"]) -> int:
        pass

    @t.overload
    def __getitem__(
            self, item: t.Literal["hits"]
    ) -> list[SearchResponseHit[T]]:
        pass

    def __getitem__(self, item):
        pass


class NodePolicy(ABC):

    @abstractmethod
    def get(self) -> str | None:
        # Returns the most relevant active node.
        pass

    def quarantine(self, node: str) -> bool:
        # Quarantines a node.
        # It can no longer be returned until it's restored.
        pass

    def restore(self, node: str) -> bool:
        # Restores a node to active duty.
        pass


class BaseRequester(ABC):

    encoder: JSONEncoder
    decoder: JSONDecoder
    headers: dict[str, str | list]
    nodes: NodePolicy

    def handle_faulty_node(self, node: str) -> None:
        pass

    @abstractmethod
    async def get(self,
                  endpoint: str,
                  *,
                  params: dict | None = None,
                  headers: dict | None = None,
                  as_json: bool = True) -> JSON | t.AnyStr | None:
        pass

    @abstractmethod
    async def post(self,
                   endpoint: str,
                   *,
                   data: dict | str | bytes | None = None,
                   params: dict | None = None,
                   headers: dict | None = None,
                   as_json: bool = True) -> JSON | t.AnyStr | None:
        pass

    @abstractmethod
    async def put(self,
                  endpoint: str,
                  *,
                  data: dict | bytes | None = None,
                  params: dict | None = None,
                  headers: dict | None = None,
                  as_json: bool = True) -> JSON | t.AnyStr | None:
        pass

    @abstractmethod
    async def patch(self,
                    endpoint: str,
                    *,
                    data: dict | bytes | None = None,
                    params: dict | None = None,
                    headers: dict | None = None,
                    as_json: bool = True) -> JSON | t.AnyStr | None:
        pass

    @abstractmethod
    async def delete(self,
                     endpoint: str,
                     *,
                     params: dict | None = None,
                     headers: dict | None = None,
                     as_json: bool = True) -> JSON | t.AnyStr | None:
        pass
