from .requester import Requester


class AnalyticsRule:

    def __init__(self, requester: Requester, rule_id: str):
        self.requester = requester
        self.rule_id = rule_id
        self.endpoint = f"/analytics/rules/{rule_id}"

    async def retrieve(self):
        return await self.requester.get(self.endpoint)

    async def delete(self):
        return await self.requester.delete(self.endpoint)

    async def upsert(self, rule: dict):
        return await self.requester.put(self.endpoint, data=rule)


class AnalyticsRules:

    endpoint: str = '/analytics/rules'

    def __init__(self, requester: Requester):
        self.requester = requester
        self.rules = {}

    def __getitem__(self, rule_id: str):
        if rule_id not in self.rules:
            self.rules[rule_id] = AnalyticsRule(self.requester, rule_id)
        return self.rules[rule_id]

    async def create(self, rule: dict, params: dict | None = None):
        return await self.requester.post(
            self.endpoint, data=rule, params=params
        )

    async def retrieve(self):
        return await self.requester.get(self.endpoint)


class Analytics:

    def __init__(self, requester: Requester):
        self.rules = AnalyticsRules(requester)
