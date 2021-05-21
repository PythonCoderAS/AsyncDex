from typing import Any, Dict, Optional, TYPE_CHECKING

from .abc import Model
from .manga_list import MangaList
from .mixins import DatetimeMixin
from ..constants import routes
from ..utils import DefaultAttrDict, copy_key_to_attribute

if TYPE_CHECKING:
    from ..client import MangadexClient


class Author(Model, DatetimeMixin):
    """A :class:`.Model` representing an individual author.

    .. note::
        Artists and authors are stored identically and share all properties.

    .. versionadded:: 0.2
    """

    name: str
    """The name of the author."""

    image: Optional[str]
    """An image of the author, if available."""

    biographies: DefaultAttrDict[Optional[str]]
    """A :class:`.DefaultAttrDict` holding the biographies of the author."""

    mangas: MangaList
    """A list of all the mangas that belong to the author.
    
    .. note::
        In order to efficiently get all mangas in one go, use:
        
        .. code-block:: python
        
            await author.load_mangas()
    """

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.mangas = MangaList(client)
        self.biographies = DefaultAttrDict(default=lambda: None)
        super().__init__(client, id=id, version=version, data=data)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "name", self)
            copy_key_to_attribute(attributes, "imageUrl", self, "image")
            if "biography" in attributes and attributes["biography"]:
                for item in attributes["biography"]:
                    for key, value in item.items():
                        self.biographies[key] = value
            self._process_times(attributes)
            self._parse_relationships(data)

    async def fetch(self):
        """Fetch data about the author. |permission| ``author.view``

        :raises: :class:`.InvalidID` if an author with the ID does not exist.
        """
        await self._fetch("author.view", "author")

    async def load_mangas(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_mangas` with the mangas that belong to the author.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_mangas(*author.mangas)
        """
        await self.client.batch_mangas(*self.mangas)

    async def update(self):
        """Update the author. |auth|

        .. versionadded:: 0.5
        """
        if not hasattr(self, "name"):
            await self.fetch()
        params = {"name": self.name, "version": self.version}
        self.client.raise_exception_if_not_authenticated("PUT", routes["author"])
        r = await self.client.request("PUT", routes["author"].format(id=self.id), json=params)
        json = await r.json()
        r.close()
        obj = type(self)(self.client, data=json)
        self.transfer(obj)

    async def delete(self):
        """Delete the author. |auth|

        .. versionadded:: 0.5
        """
        return await self._delete("author")
