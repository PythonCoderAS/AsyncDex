from datetime import datetime
from typing import Optional, Union

import aiohttp


class AsyncDexException(Exception):
    """Base exception class for all exceptions by the package."""


class Ratelimit(AsyncDexException):
    """An exception raised if :attr:`sleep_on_ratelimit` is set to False."""

    path: str
    """The route that was taken that hit the ratelimit. This will match the path in the MangaDex API Documentation."""

    ratelimit_amount: int
    """How many calls to this path can be made once the ratelimit expires without being ratelimited again."""

    ratelimit_expires: datetime
    """A :class:`datetime.datetime` object in UTC time representing when the ratelimit will expire."""

    def __init__(self, path: str, ratelimit_amount: int, ratelimit_expires: datetime):
        self.path = path
        self.ratelimit_amount = ratelimit_amount
        self.ratelimit_expires = ratelimit_expires


class HTTPException(AsyncDexException):
    """Exceptions for HTTP status codes."""

    path: str
    """The URL taken that hit the error."""

    response: aiohttp.ClientResponse
    """The :class:`aiohttp.ClientResponse` object from the request."""

    def __init__(self, path: str, response: aiohttp.ClientResponse):
        self.path = path
        self.response = response


class Unauthorized(HTTPException):
    """An exception raised if a request to an endpoint requiring authorization is made where the client cannot authorize using provided
    information."""

    response: Optional[aiohttp.ClientResponse]
    """The :class:`aiohttp.ClientResponse` object from the request. May be ``None`` if a user tries to login without stored credentials."""

    def __init__(self, path: str, response: Optional[aiohttp.ClientResponse]):
        self.path = path
        self.response = response
