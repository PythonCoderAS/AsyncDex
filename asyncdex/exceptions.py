from datetime import datetime
from typing import Optional, TYPE_CHECKING, Type

import aiohttp

if TYPE_CHECKING:
    from .models.abc import Model


class AsyncDexException(Exception):
    """Base exception class for all exceptions by the package."""


class Ratelimit(AsyncDexException):
    """An exception raised if :attr:`MangadexClient.sleep_on_ratelimit` is set to False."""

    path: str
    """The route that was taken that hit the ratelimit. This will match the path in the MangaDex API Documentation."""

    ratelimit_amount: int
    """How many calls to this path can be made once the ratelimit expires without being ratelimited again."""

    ratelimit_expires: datetime
    """A :class:`datetime.datetime` object in UTC time representing when the ratelimit will expire."""

    def __init__(self, path: str, ratelimit_amount: int, ratelimit_expires: datetime):
        super().__init__(
            f"Ratelimited for {(ratelimit_expires - datetime.utcnow()).total_seconds():.3d} seconds on " f"{path}."
        )
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
        super().__init__(f"HTTP Error on {path}.")
        self.path = path
        self.response = response


class Unauthorized(HTTPException):
    """An exception raised if a request to an endpoint requiring authorization is made where the client cannot
    authorize using provided information."""

    response: Optional[aiohttp.ClientResponse]
    """The :class:`aiohttp.ClientResponse` object from the request. May be ``None`` if a user tries to login without 
    stored credentials."""

    def __init__(self, path: str, response: Optional[aiohttp.ClientResponse]):
        AsyncDexException.__init__(self, f"Unauthorized for path {path}.")
        self.path = path
        self.response = response


class Missing(AsyncDexException):
    """An exception raised if a response is missing a critical element for a model.

    .. versionadded:: 0.2

    :param model: The name of the model that requires the attribute. Can be empty.
    :type model: str
    """

    attribute: str
    """The name of the attribute that is missing."""

    def __init__(self, attribute: str, model: Optional[str] = None):
        if model:
            super().__init__(f"The {attribute!r} attribute is required for {model!r} but is not found.")
        else:
            super().__init__(f"The {attribute!r} attribute is required but is not found.")
        self.attribute = attribute


class InvalidID(AsyncDexException):
    """An exception raised if an invalid ID is given to any of the ``get_*`` methods representing that an item with
    this ID does not exist.

    .. versionadded:: 0.2
    """

    id: str
    """The given ID"""

    model: Type["Model"]
    """The model that would have been returned had the ID been valid."""

    def __init__(self, id: str, model: Type["Model"]):
        super().__init__(f"There is no {model.__name__} with the UUID {id!r}.")
        self.id = id
        self.model = model
