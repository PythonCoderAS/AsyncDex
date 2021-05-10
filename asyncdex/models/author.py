from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .abc import Model
from .mixins import DatetimeMixin
from ..utils import DefaultAttrDict, copy_key_to_attribute

if TYPE_CHECKING:
    from ..client import MangadexClient
    from .manga import Manga


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

    mangas: List["Manga"]
    """A list of all the mangas that the author has written.
    
    .. note::
        In order to efficiently get all mangas in one go, use:
        
        .. code-block:: python
        
            await client.batch_mangas(*author.mangas)
    """

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.mangas = []
        self.biographies = DefaultAttrDict(default=lambda: None)
        super().__init__(client, id=id, version=version, data=data)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "name", self)
            copy_key_to_attribute(attributes, "imageUrl", self, "image")
            if "biography" in attributes:
                for item in attributes["biography"]:
                    for key, value in item.items():
                        self.biographies[key] = value
            self._process_times(attributes)
            self._parse_relationships(data)

    async def fetch(self):
        await self._fetch("author")

    async def load_mangas(self):
        """Shortcut method that calls :meth:`.Client.batch_mangas` with the mangas that belong to the author.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_mangas(*author.mangas)
        """
        await self.client.batch_mangas(*self.mangas)
