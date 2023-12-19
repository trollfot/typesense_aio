from .requester import Requester


class Alias:

    def __init__(self, requester: Requester, name: str):
        self.requester = requester
        self.name = name
        self.endpoint: str = f'/aliases/{name}'

    def retrieve(self):
        return self.requester.get(self.endpoint)

    def delete(self):
        return self.requester.delete(self.endpoint)

    def upsert(self, mapping: dict):
        return self.requester.put(self.endpoint, data=mapping)


class Aliases:

    endpoint: str = '/aliases'

    def __init__(self, requester: Requester):
        self.requester = requester
        self.aliases = {}

    def __getitem__(self, name):
        if name not in self.aliases:
            self.aliases[name] = Alias(self.requester, name)
        return self.aliases.get(name)

    def retrieve(self):
        return self.requester.get(self.endpoint)
