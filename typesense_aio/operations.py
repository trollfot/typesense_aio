from .requester import Requester


class Operations:
    endpoint: str = ''

    def __init__(self, requester: Requester):
        self.requester = requester

    def perform(self, operation_name: str, params: dict | None = None):
        endpoint = f'/operations/{operation_name}'
        return self.requester.post(endpoint, params=params)
