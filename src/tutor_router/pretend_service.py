"""Pretend services.

Scenario: you have several remote TutorRouter devices and need to figure out the busiest by calculating the total
ingress and egress of each. At first this is easily done with a simple script but owing to security concerns, a later
version of firmware has been rolled out that change the API. The rollout cannot be across the board: some have been
upgraded, some haven't.

Sequence of events:
  * All TutorRouters are the same. Use single script to iterate over all TutorRouters' IPs, login to each and get
    traffic data.
  * New TutorRouter firmware is rolled out to some. Script can no longer log in or get traffic data. Modify script
    with if/else.
    * Observe that further firmware updates will cause headaches...
    * Observe that other scripts doing different tasks will have to be modified.

Demonstrate:
    * Inheritance - DRYness.
        * Each device _is a_ TutorRouter with some commonalities, e.g. IP address; healthcheck is always the same.
        * All TutorRouters can output total ingress and total egress.
        * Different login methodologies.
    * Encapsulation - contain attributes (properties and methods) together.
        * Each device _has an_ IP address.
    * Abstraction - hide implementation details.
        * Determine remote firmware.
        * Create LoginMethodology based on remote type.
    * Polymorphism
        * Make the same calls on all TutorRouters.

"""
import abc
import json
import random
from uuid import uuid4
from urllib.parse import urlparse


class NotFoundError(Exception):
    pass


class TutorRouter(abc.ABC):
    """Abstract remote router."""

    # Don't use this in multiprocessing or async ;-)
    COUNTER = 1

    # shortcuts to return to caller
    SHORTCUT_STATUS = {
        "ok": (200, json.dumps({"message": "OK"})),
        "forbidden": (403, json.dumps({"message": "Forbidden"})),
        "not found": (404, json.dumps({"message": "Not Found"})),
    }

    def __init__(self):
        self._healthy = random.random() > 0.25
        self._hostname = f"TutorRouter-{TutorRouter.COUNTER}"
        self._auth_token = str(uuid4())
        TutorRouter.COUNTER += 1
        self._interfaces = {
            "eth0": self._create_interface_data(),
            "mgmt": self._create_interface_data(),
        }

    @abc.abstractmethod
    def _login_headers(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _login_path(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _health_indicator(self, health: bool):
        raise NotImplementedError()

    @abc.abstractmethod
    def _version(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _check_auth(self, headers):
        raise NotImplementedError()

    @staticmethod
    def _create_interface_data():
        return {
            "up": random.randint(1_000, 1_000_000),
            "down": random.randint(1_000, 1_000_000),
        }

    @staticmethod
    def _obscured_count(count):
        return count

    def _obscured_interfaces(self):
        """Make life harder for callers :-)"""
        return {
            name: {
                direction: self._obscured_count(count)
                for direction, count in data.items()
            }
            for name, data in self._interfaces.items()
        }

    def _all_interfaces_data(self):
        return json.dumps(self._obscured_interfaces())

    def _healthcheck(self):
        return json.dumps({
            "host": self._hostname,
            "version": self._version(),
            "health": self._health_indicator(self._healthy)
        })

    @property
    def hostname(self):
        return self._hostname

    def post(self, path, headers=None) -> (int, str):
        headers = headers or {}
        if path == self._login_path():
            if headers == self._login_headers():
                return 200, self._auth_token
            else:
                return self.SHORTCUT_STATUS["forbidden"]
        return self.SHORTCUT_STATUS["forbidden"]

    def get(self, url, headers=None) -> (int, str):
        parsed_url = urlparse(url)
        headers = headers or {}

        if parsed_url.path == "healthcheck":
            if self._healthy:
                return 200, self._healthcheck()
            else:
                raise NotFoundError(f"Connection error")

        # Anything except healthcheck requires login.
        if not self._check_auth(headers):
            return self.SHORTCUT_STATUS["forbidden"]

        # "interfaces" return names of all interfaces
        if parsed_url.path == "interfaces":
            return 200, self._all_interfaces_data()

        return self.SHORTCUT_STATUS["not found"]


class TutorRouterV1(TutorRouter):

    def _health_indicator(self, health: bool):
        return {False: "bad", True: "good"}[health]

    def _login_path(self):
        return "login"

    def _login_headers(self):
        return {"username": "admin", "password": "Password123"}

    def _check_auth(self, headers):
        return headers.get("Token") == f"{self._auth_token}"

    def _version(self):
        return 1


class TutorRouterV2(TutorRouter):

    def _health_indicator(self, health: bool):
        return {False: "warn", True: "ok"}[health]

    def _login_path(self):
        return "authenticate/admin"

    def _login_headers(self):
        return {"token": "Password123"}

    def _check_auth(self, headers):
        return headers.get("Authentication") == f"TOKEN {self._auth_token}"

    def _version(self):
        return 2

    @staticmethod
    def _obscured_count(count):
        return f"{int(count / 1000)} Kbps"
