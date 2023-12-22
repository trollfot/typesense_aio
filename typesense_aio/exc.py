import httpx


class TypesenseClientError(IOError):
    pass


class Timeout(TypesenseClientError):
    pass


class RequestMalformed(TypesenseClientError):
    pass


class RequestUnauthorized(TypesenseClientError):
    pass


class RequestForbidden(TypesenseClientError):
    pass


class ObjectNotFound(TypesenseClientError):
    pass


class ObjectAlreadyExists(TypesenseClientError):
    pass


class ObjectUnprocessable(TypesenseClientError):
    pass


class ServerError(TypesenseClientError):
    pass


class ServiceUnavailable(TypesenseClientError):
    pass


class HTTPStatus0Error(TypesenseClientError):
    pass


class InvalidParameter(TypesenseClientError):
    pass


service_exceptions = (
    httpx.RequestError,
    httpx.ConnectTimeout,
    HTTPStatus0Error,
    ServerError,
    ServiceUnavailable
)

exceptions_mapping = {
    0: HTTPStatus0Error,
    400: RequestMalformed,
    401: RequestUnauthorized,
    403: RequestForbidden,
    404: ObjectNotFound,
    409: ObjectAlreadyExists,
    422: ObjectUnprocessable,
    500: ServerError,
    503: ServiceUnavailable
}


def resolve_exception(status_code: int):
    return exceptions_mapping.get(status_code, TypesenseClientError)
