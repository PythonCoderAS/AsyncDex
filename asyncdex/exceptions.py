from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING, Type

import aiohttp
from aiohttp import ClientResponseError

from .constants import routes
from .utils import AttrDict

if TYPE_CHECKING:  # pragma: no cover
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
            f"Ratelimited for {(ratelimit_expires - datetime.utcnow()).total_seconds():.3f} seconds on {path}."
        )
        self.path = path
        self.ratelimit_amount = ratelimit_amount
        self.ratelimit_expires = ratelimit_expires


class HTTPException(AsyncDexException, ClientResponseError):
    """Exceptions for HTTP status codes."""

    method: str
    """The HTTP method that caused the exception.
    
    .. versionadded:: 0.5
    """

    path: str
    """The URL taken that hit the error."""

    response: Optional[aiohttp.ClientResponse]
    """The :class:`aiohttp.ClientResponse` object from the request. May be ``None``.
    
    .. versionchanged:: 1.0
        The response may be ``None``.
    """

    json: Optional[Dict[str, List[AttrDict[str]]]]
    """The JSON object returned by the server if there is a response."""

    def __init__(
        self,
        method: str,
        path: str,
        response: Optional[aiohttp.ClientResponse],
        *,
        json: Optional[Dict[str, List[Dict[str, str]]]] = None,
        msg: str = "HTTP Error on {method} for {path}.",
    ):
        self.json = json
        if json and json.get("errors", None):
            self.json["errors"] = [AttrDict(item) for item in self.json["errors"]]
        if self.json:
            primary_error = self.json["errors"][0]
            msg = "{primary_error.title}: {primary_error.detail}"
            if getattr(primary_error, "context", None):
                msg += " ({primary_error.context})"
        if response:
            super().__init__(
                response.request_info,
                response.history,
                status=response.status,
                headers=response.headers,
                message=msg.format(**locals()),
            )
        else:
            super().__init__(None, None, message=msg.format(**locals()))
        self.path = path
        self.response = response

    def __repr__(self) -> str:
        msg = self.message
        if self.response:
            msg = f"HTTP {self.response.status}: " + msg
        return msg

    def __str__(self) -> str:
        return self.__repr__()


class Unauthorized(HTTPException):
    """An exception raised if a request to an endpoint requiring authorization is made where the client cannot
    authorize using provided information."""

    response: Optional[aiohttp.ClientResponse]
    """The :class:`aiohttp.ClientResponse` object from the request. May be ``None`` if a user tries to login without 
    stored credentials."""

    def __init__(
        self,
        method: str,
        path: str,
        response: Optional[aiohttp.ClientResponse],
        *,
        json: Optional[Dict[str, List[Dict[str, str]]]] = None,
    ):
        super().__init__(method, path, response, msg="Unauthorized for {method} on {path}.", json=json)


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


class PermissionMismatch(HTTPException):
    """An exception raised if the current user does not have a certain permission.

    .. versionadded:: 0.5
    """

    permission: str
    """The permission node the user is lacking."""

    response: Optional[aiohttp.ClientResponse]
    """The :class:`aiohttp.ClientResponse` object from the request. May be ``None`` if a user tries to login without 
    stored credentials."""

    def __init__(self, permission: str, method: str, path: str, response: Optional[aiohttp.ClientResponse]):
        super().__init__(method, path, response, msg="Missing permission %s for {method} on {path}." % permission)
        self.permission = permission


class Captcha(HTTPException):
    """An exception raised if a captcha solve is required to proceed.

    .. versionadded:: 0.5

    .. admonition:: Solving reCaptchas with AsyncDex:

        AsyncDex will raise the Captcha exception to any request that prompts for a captcha. Afterwards,
        it is necessary to call :meth:`.solve_captcha` with the correct captcha response, and then retry whatever
        request caused the captcha.
    """

    site_key: str
    """The captcha sitekey to solve."""

    def __init__(
        self,
        site_key: str,
        method: str,
        path: str,
        response: aiohttp.ClientResponse,
    ):
        super().__init__(method, path, response, msg="Captcha required for {method} on {path}")
        self.site_key = site_key


class InvalidCaptcha(HTTPException):
    """An exception raised if an attempt to solve a captcha was invalid.

    .. versionadded:: 0.5
    """

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        *,
        json: Optional[Dict[str, List[Dict[str, str]]]] = None,
    ):
        super().__init__("POST", routes["captcha"], response, msg="Invalid captcha solve.", json=json)
