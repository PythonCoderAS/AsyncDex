from typing import Any, Dict

from .abc import Model
from .manga_list import MangaList
from .mixins import DatetimeMixin
from .user import User
from ..constants import routes
from ..enum import Visibility
from ..utils import copy_key_to_attribute


class CustomList(Model):
    """A :class:`.Model` representing a custom list.

    .. versionadded:: 0.5
    """

    name: str
    """The name of the custom list."""

    visibility: Visibility

    mangas: MangaList
    """A list of all the mangas that belong to the custom list.

    .. note::
        In order to efficiently get all mangas in one go, use:

        .. code-block:: python

            await clist.load_mangas()
    """

    owner: User
    """The creator of the custom list."""

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "name", self)
            copy_key_to_attribute(attributes, "visibility", self, transformation=lambda item: Visibility(item))
            copy_key_to_attribute(
                attributes, "owner", self, transformation=lambda item: User(self.client, data={"data": item})
            )
            self._parse_relationships(data)

    async def fetch(self):
        self.client.raise_exception_if_not_authenticated("GET", routes["list"])
        await self._fetch(None, "list")

    async def load_mangas(self):
        """Shortcut method that calls :meth:`.Client.batch_mangas` with the mangas that belong to the author.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_mangas(*author.mangas)
        """
        await self.client.batch_mangas(*self.mangas)
