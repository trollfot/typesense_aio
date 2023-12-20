from .health import Health
from .keys import Keys
from .collections import Collections
from .config import Configuration
from .requester import Requester
from .multisearch import MultiSearch
from .aliases import Aliases
from .analytics import Analytics
from .debug import Debug
from .nodes import Nodes


class Client:

    def __init__(self, config: Configuration):
        requester = Requester(config)
        self.aliases: Aliases = Aliases(requester)
        self.analytics: Analytics = Analytics(requester)
        self.collections: Collections = Collections(requester)
        self.health: Health = Health(requester)
        self.debug: Debug = Debug(requester)
        self.keys: Keys = Keys(requester)
        self.multi_search: MultiSearch = MultiSearch(requester)
