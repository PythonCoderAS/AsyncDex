import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import getLogger
from math import ceil
from re import Pattern
from typing import Dict, Optional, Tuple

import aiohttp

logger = getLogger(__name__)


@dataclass(frozen=True)
class Path:
    """A Path object representing a various path."""

    name: str
    """The name of the path. This will be the value provided by :attr:`.Ratelimit.path`."""
    path_regex: Pattern
    """A compiled regex pattern matching the path, used when the path has a variable, such as ``/action/{id}``."""
    method: Optional[str] = None
    """The HTTP method for the path. Leave None if ratelimit applies to all methods."""


@dataclass()
class PathRatelimit:
    """An object that allows the request method to check the ratelimit before making a response."""

    path: Path
    """A :class:`~.Path` object."""
    ratelimit_amount: int
    """Analogous to :attr:`.Ratelimit.ratelimit_amount`"""
    ratelimit_time: int
    """The amount of time needed for the ratelimit to expire after the first use."""
    ratelimit_expires: datetime = field(default=datetime.min, init=False)
    """Analogous to :attr:`.Ratelimit.ratelimit_expires`"""
    ratelimit_used: int = field(default=0, init=False)
    """How many times the path has been called since the last ratelimit expire."""
    ratelimit_enqueued: int = field(default=0, init=False)
    """How many requests are currently sleeping. This is used to up the sleep time to prevent a number of requests 
    more than double the ``ratelimit_time`` amount of requests."""

    def time_until_expire(self) -> timedelta:
        """Returns a :class:`datetime.timedelta` representing the amount of seconds for the ratelimit to expire."""
        return self.ratelimit_expires - datetime.utcnow()

    def can_call(self, method: str) -> bool:
        """Returns whether or not this route can be used right now.

        :param method: The HTTP method being used.
        :type method: str
        :return: Whether or not this route can be used without ratelimit.
        :rtype: bool
        """
        if self.path.method == method or self.path.method is None:
            return self.ratelimit_used < self.ratelimit_amount or self.time_until_expire() < timedelta(microseconds=-1)
        else:
            return True

    def expire(self):
        """Expire the ratelimit."""
        self.ratelimit_used = 0
        self.ratelimit_expires = datetime.min

    def update(self, response: aiohttp.ClientResponse):
        """Update the path's ratelimit based on the headers.

        :param response: The response object.
        :type response: aiohttp.ClientResponse
        """
        headers = response.headers
        if self.ratelimit_expires == datetime.min:
            self.ratelimit_expires = datetime.utcnow() + timedelta(seconds=self.ratelimit_time)
        if headers.get("x-ratelimit-limit", ""):
            self.ratelimit_amount = int(headers["x-ratelimit-limit"])
        if headers.get("x-ratelimit-retry-after", ""):
            new_ratelimit = datetime.utcfromtimestamp(int(headers["x-ratelimit-retry-after"]))
            if new_ratelimit > self.ratelimit_expires:
                self.ratelimit_expires = new_ratelimit
        if headers.get("x-ratelimit-remaining", ""):
            self.ratelimit_used = self.ratelimit_amount - int(headers["x-ratelimit-remaining"])
        else:
            self.ratelimit_used += 1


class Ratelimits:
    """An object holding all of the various ratelimits.

    :param ratelimits: The :class:`.PathRatelimit` object.
    :type ratelimits: PathRatelimit
    """

    ratelimit_dictionary: Dict[Pattern, PathRatelimit]
    """A dictionary where the keys are regex patterns representing the paths and the values are 
    :class:`~.PathRatelimit` objects."""

    def __init__(self, *ratelimits: PathRatelimit):
        self.ratelimit_dictionary = {}
        self._check_lock = asyncio.Lock()
        self._enqueue_lock = asyncio.Lock()
        for item in ratelimits:
            self.add(item)

    def add(self, obj: PathRatelimit):
        """Add a new ratelimit. If the path is the same as an existing path, it will be overwritten.

        :param obj: The new ratelimit object to add.
        :type obj: PathRatelimit
        """
        self.ratelimit_dictionary[obj.path.path_regex] = obj

    def remove(self, obj: PathRatelimit):
        """Remove a ratelimit.

        :param obj: The new ratelimit object to remove.
        :type obj: PathRatelimit
        """
        self.ratelimit_dictionary.pop(obj.path.path_regex)

    async def check(self, url: str, method: str) -> Tuple[float, Optional[PathRatelimit]]:
        """Check if a path is ratelimited.

        :param url: The path, starting with ``/``
        :type url: str
        :param method: The HTTP method being used.
        :type method: str
        :return: A number representing the amount of seconds before ratelimit expire or -1 if there is no need to
            ratelimit as well as the :class:`~.PathRatelimit` object if found.
        :rtype: float
        """
        # We want to check with priority.
        # For example, ``/url/x/something`` matches both ``/url/{id}`` and ``/url/{id}/something``.
        # We want to match the second one because that is how API ratelimits work.
        ratelimit_obj = None
        obj_priority = 0  # Actually just the number of slashes in the regex
        async with self._check_lock:
            for regex, obj in self.ratelimit_dictionary.items():
                if regex.match(url):
                    count = regex.pattern.count("/")
                    if count > obj_priority:
                        obj_priority = count
                        ratelimit_obj = obj
            if ratelimit_obj is None:
                return -1, ratelimit_obj
            if ratelimit_obj.can_call(method):
                return -1, ratelimit_obj
            return (
                ceil(
                    ratelimit_obj.time_until_expire().total_seconds()
                    + (ratelimit_obj.ratelimit_time * ((ratelimit_obj.ratelimit_enqueued // 60)) + 1)
                ),
                ratelimit_obj,
            )

    async def sleep(self, url: str, method: str) -> Optional[PathRatelimit]:
        """Helper function that sleeps the amount of time returned by :meth:`.check`.

        :param url: The path, starting with ``/``
        :type url: str
        :param method: The HTTP method being used.
        :type method: str
        :return: The :class:`~.PathRatelimit` object if found
        :rtype: :class:`~.PathRatelimit`
        """
        time_to_sleep, retval = await self.check(url, method)
        if time_to_sleep > 0:
            async with self._enqueue_lock:
                retval.ratelimit_enqueued += 1
            logger.warning("Sleeping for %s seconds.", time_to_sleep)
            await asyncio.sleep(time_to_sleep)
            async with self._enqueue_lock:
                retval.ratelimit_enqueued -= 1
        return retval

    def __repr__(self) -> str:
        """Provide a string representation of the object.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}{self.ratelimit_dictionary!r}"
