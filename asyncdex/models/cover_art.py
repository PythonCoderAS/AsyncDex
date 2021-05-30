from typing import Any, Dict, Optional, TYPE_CHECKING

from .abc import Model
from .mixins import DatetimeMixin
from .user import User
from ..constants import routes
from ..utils import copy_key_to_attribute

if TYPE_CHECKING:
    from .manga import Manga
    from .user import User


class CoverArt(Model, DatetimeMixin):
    """A :class:`.Model` representing an individual cover art.

    .. versionadded:: 1.0
    """

    description: str
    """The description of the cover art."""

    volume: Optional[str]
    """The volume that this cover art represents."""

    file_name: Optional[str]
    """The name of the file that contains the cover art."""

    manga: Optional["Manga"]
    """The manga that this cover art belongs to."""

    user: Optional["User"]
    """The user that this cover art belongs to."""

    async def url(self) -> str:
        """Get a URL to the cover.

        :return: The URL.
        :rtype: str
        """
        if not hasattr(self, "file_name"):
            await self.fetch()
        return f"https://uploads.mangadex.org/covers/{self.manga.id}/{self.file_name}"

    async def url_512(self) -> str:
        """Get the <=512 px URL to the cover.

        :return: The URL.
        :rtype: str
        """
        return await self.url() + ".512.jpg"

    async def url_256(self) -> str:
        """Get the <=256 px URL to the cover.

        :return: The URL.
        :rtype: str
        """
        return await self.url() + ".256.jpg"

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "name", self)
            self._process_times(attributes)
        self._parse_relationships(data)
        if hasattr(self, "_users"):
            self.user = self._users[0]
            del self._users
        if hasattr(self, "mangas"):
            self.manga = self.mangas[0]
            del self.mangas

    async def fetch(self):
        """Fetch data about the chapter. |permission| ``cover.view``

        :raises: :class:`.InvalidID` if a cover with the ID does not exist.
        """
        await self._fetch("cover.view", "cover")

    async def update(self):
        """Update the cover. |auth|"""
        params = {"volume": self.volume, "description": self.description, "version": self.version}
        self.client.raise_exception_if_not_authenticated("PUT", routes["cover"])
        r = await self.client.request("PUT", routes["cover"].format(id=self.id), json=params)
        json = await r.json()
        r.close()
        obj = type(self)(self.client, data=json)
        self.transfer(obj)

    async def delete(self):
        """Delete the cover. |auth|"""
        return await self._delete("cover")
