import random
from .pretend_service import TutorRouterV1, TutorRouterV2, NotFoundError


class Scenario:
    """Build a tutorial scenario and provide `requests`-like methods."""
    def __init__(self, name, routers):
        self._name = name
        self._routers = routers

    @staticmethod
    def scenario_1():
        return Scenario(
            "Scenario 1",
            {router.hostname: router for router in (TutorRouterV1() for _ in range(20))}
        )

    @staticmethod
    def scenario_2():
        return Scenario(
            "Scenario 2",
            {
                router.hostname: router
                for router in (
                    (TutorRouterV1 if random.random() < 0.5 else TutorRouterV2)()
                    for _ in range(20)
                )
            }
        )

    def hosts(self):
        return list(self._routers.keys())

    def request(self, hostname, method, path, headers=None):
        try:
            router = self._routers[hostname]
        except KeyError:
            raise NotFoundError(f"Connection error: {hostname}")

        method = method.lower()

        if method == "get":
            return router.get(path, headers)

        if method == "post":
            return router.post(path, headers)

    def get(self, hostname, path, headers=None):
        return self.request(hostname, "GET", path, headers)

    def post(self, hostname, path, headers=None):
        return self.request(hostname, "POST", path, headers)
