"""Contains ABCs for the various models"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TYPE_CHECKING, TypeVar

from aiohttp import ClientResponse

from ..constants import routes
from ..exceptions import InvalidID, Missing
from ..utils import copy_key_to_attribute, parse_relationships

if TYPE_CHECKING:
    from ..client import MangadexClient

_T = TypeVar("_T", bound="Model")


class Model(ABC):
    """An abstract model. Cannot be instantiated.

    .. versionadded:: 0.2

    :raises: :class:`.Missing` if there is no valid ID in the model after parsing provided data.
    :param data: The data received from the server. May be None if there is no data yet.
    :type data: Dict[str, Any]
    """

    id: str
    """A `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`_ that represents this item."""

    version: int
    """The version of the model."""

    client: "MangadexClient"
    """The client that created this model."""

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.client = client
        self.id = id
        self.version = version
        if data:
            self.parse(data)
        if not self.id:
            raise Missing("id", type(self).__name__)

    @abstractmethod
    def parse(self, data: Dict[str, Any]):
        """Parse the data received from the server.

        :param data: The data from the server.
        :type data: Dict[str, Any]
        """
        if "result" in data:
            assert data["result"] == "ok"
        if "data" in data:
            copy_key_to_attribute(data["data"], "id", self)
            if "attributes" in data["data"]:
                copy_key_to_attribute(
                    data["data"]["attributes"], "version", self, transformation=lambda num: int(num) if num else num
                )

    @abstractmethod
    async def fetch(self):
        """Fetch the data to complete any missing non-critical values.

        :raises: :class:`.InvalidID` if an object with the ID does not exist.
        """

    def __str__(self) -> str:
        """Returns a string representation of the model, usually it's id."""
        return self.id

    def __repr__(self) -> str:
        """Returns a string version of the model useful for development."""
        return f"{type(self).__name__}(id={self.id!r})"

    def __eq__(self: _T, other: _T) -> bool:
        """Check if two models are equal to each other.

        :param other: Another model. Should be the same type as the model being compared.
        :type other: Model
        :return: Whether or not the models are equal.
        :rtype: bool
        """
        if isinstance(other, type(self)):
            return (self.id, self.version, self.client) == (other.id, other.version, other.client)
        return NotImplemented

    def __ne__(self: _T, other: _T) -> bool:
        """Check if two models are not equal to each other.

        :param other: Another model. Should be the same type as the model being compared.
        :type other: Model
        :return: Whether or not the models are equal.
        :rtype: bool
        """
        # This is faster because OR will short-circuit on the first or second condition, which is the case for 99% of
        # comparisons.
        if type(self) == type(other):
            return (self.id, self.version, self.client) != (other.id, other.version, other.client)
        return NotImplemented

    def transfer(self: _T, new_obj: _T):
        """Transfer data from a new object to the current object.

        :param new_obj: The new object. Should be the same type as the current model.
        :type new_obj: Model
        """
        if type(self) != type(new_obj):
            raise ValueError(f"Expected 'new_obj' to be {type(self).__name__!r}, got {type(new_obj).__name__!r}.")
        if new_obj.version > self.version:
            for attribute, value in vars(new_obj).items():
                if value != getattr(self, attribute, None):
                    setattr(self, attribute, value)

    def _parse_relationships(self, data: dict):
        parse_relationships(data, self)

    def _check_404(self, r: ClientResponse):
        if r.status == 404:
            raise InvalidID(self.id, type(self))

    async def _fetch(self, permission: Optional[str], route_name: str):
        if permission:
            self.client.user.permission_exception(permission, "GET", routes[route_name])
        r = await self.client.request("GET", routes[route_name].format(id=self.id))
        self._check_404(r)
        self.parse(await r.json())
        r.close()

    def __hash__(self):
        return hash((self.id, self.version, self.client))

    async def _delete(self, route_name: str):
        self.client.raise_exception_if_not_authenticated("DELETE", routes[route_name])
        await self.client.request("DELETE", routes[route_name].format(id=self.id))


class ModelList(ABC, List[_T], Generic[_T]):
    """An ABC representing a list of models.

    .. note::
        Models of different types should not be combined, meaning placing a Manga and a Chapter into the same list is
        invalid and will lead to undefined behavior.

    .. versionadded:: 0.5
    """

    def id_map(self) -> Dict[str, _T]:
        """Return a mapping of item UUID to items.

        .. versionadded:: 0.5

        :return: A dictionary where the keys are strings and the values are :class:`Model` objects.
        :rtype: Dict[str, Model]
        """
        return {item.id: item for item in self}

    async def fetch_all(self):
        """Fetch all models.

        .. versionadded:: 0.5
        """
        from .manga import Manga
        from .chapter import Chapter
        from .group import Group
        from .author import Author

        if self:
            if isinstance(self[0], Manga):
                await self[0].client.batch_mangas(*self)
            elif isinstance(self[0], Chapter):
                await self[0].client.batch_chapters(*self)
            elif isinstance(self[0], Group):
                await self[0].client.batch_groups(*self)
            elif isinstance(self[0], Author):
                await self[0].client.batch_authors(*self)
            else:
                await asyncio.gather(*[asyncio.create_task(item.fetch()) for item in self])


class GenericModelList(ModelList[_T], Generic[_T]):
    """A class representing a generic list of models with no special methods.

    .. versionadded:: 0.5
    """
