import asyncio
from typing import Iterable, Optional, TYPE_CHECKING

from .abc import ModelList
from ..constants import routes
from ..enum import FollowStatus

if TYPE_CHECKING:
    from ..client import MangadexClient
    from .manga import Manga


class MangaList(ModelList["Manga"]):
    """An object representing a list of manga.

    .. versionadded:: 0.5
    """

    client: "MangadexClient"
    """The client that this manga list belongs to."""

    def __init__(self, client: "MangadexClient", *, entries: Optional[Iterable["Manga"]] = None):
        super().__init__(entries or [])
        self.client = client

    async def fetch_all(self):
        return await self.client.batch_mangas(*self)

    async def get_reading_status(self):
        """Get the reading status of all manga in the list. |auth|"""
        self.client.raise_exception_if_not_authenticated("GET", routes["logged_user_manga_status"])
        r = await self.client.request("GET", routes["logged_user_manga_status"])
        json = await r.json()
        r.close()
        map = self.id_map()
        for uuid, val in json["statuses"].items():
            if uuid in map:
                map[uuid].reading_status = FollowStatus(val)

    async def set_reading_status(self, status: Optional[FollowStatus]):
        """Sets the reading status of all manga in the list. Requires authentication.

        :param status: The new status to set. Can be None to remove reading status.
        :type status: Optional[FollowStatus]
        :raises: :class:`.Unauthorized` is authentication is missing.
        """
        await asyncio.gather(*[item.set_reading_status(status) for item in self])
