from .health import Health
from .keys import Keys
from .collections import Collections
from .config import Configuration
from .requester import Requester
from .multisearch import MultiSearch


class Client:

    def __init__(self, config: Configuration):
        requester = Requester(config)
        self.health: Health = Health(requester)
        self.collections: Collections = Collections(requester)
        self.keys: Keys = Keys(requester)
        self.multi_search = MultiSearch(requester)
