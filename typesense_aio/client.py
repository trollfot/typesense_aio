from .aliases import Aliases
from .analytics import Analytics
from .collections import Collections
from .config import Configuration
from .debug import Debug
from .health import Health
from .keys import Keys
from .multisearch import MultiSearch
from .operations import Operations
from .requester import Requester


class Client:

    def __init__(self, config: Configuration):
        self.requester = Requester(config)
        self.aliases: Aliases = Aliases(self.requester)
        self.analytics: Analytics = Analytics(self.requester)
        self.collections: Collections = Collections(self.requester)
        self.health: Health = Health(self.requester)
        self.debug: Debug = Debug(self.requester)
        self.keys: Keys = Keys(self.requester)
        self.multi_search: MultiSearch = MultiSearch(self.requester)
        self.operations: Operations = Operations(self.requester)

    def log_slow_request(self, threshold: int = 2000):
        # -1 disables it.
        return self.requester.post('/config', data={
            "log-slow-requests-time-ms": threshold
        })

    def get_metrics(self):
        return self.requester.get('/metrics.json')

    def get_stats(self):
        return self.requester.get('/stats.json')
