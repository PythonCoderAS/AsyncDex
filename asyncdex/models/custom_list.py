from datetime import datetime
from typing import Any, Dict, List, Optional

from .abc import Model
from .chapter import Chapter
from .manga_list import MangaList
from .pager import Pager
from .user import User
from ..constants import routes
from ..enum import Visibility
from ..list_orders import MangaFeedListOrder
from ..utils import copy_key_to_attribute, return_date_string


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
        """Fetch data about the list. |auth|"""
        self.client.raise_exception_if_not_authenticated("GET", routes["list"])
        await self._fetch(None, "list")

    async def load_mangas(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_mangas` with the mangas that belong to the author.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_mangas(*author.mangas)
        """
        await self.client.batch_mangas(*self.mangas)

    def manga_chapters(
        self,
        *,
        languages: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        published_after: Optional[datetime] = None,
        order: Optional[MangaFeedListOrder] = None,
        limit: Optional[int] = None,
    ) -> Pager[Chapter]:
        """Get the chapters from the manga in the custom list. |auth|

        .. versionadded:: 0.5

        :param languages: The languages to filter by.
        :type languages: List[str]
        :param created_after: Get chapters created after this date.

            .. note::
                The datetime object needs to be in UTC time. It does not matter if the datetime if naive or timezone
                aware.

        :type created_after: datetime
        :param updated_after: Get chapters updated after this date.

            .. note::
                The datetime object needs to be in UTC time. It does not matter if the datetime if naive or timezone
                aware.

        :type updated_after: datetime
        :param published_after: Get chapters published after this date.

            .. note::
                The datetime object needs to be in UTC time. It does not matter if the datetime if naive or timezone
                aware.

        :type published_after: datetime
        :param order: The order to sort the chapters.
        :type order: MangaFeedListOrder
        :param limit: Only return up to this many chapters.

            .. note::
                Not setting a limit when you are only interested in a certain amount of responses may result in the
                Pager making more requests than necessary, consuming ratelimits.

        :type limit: int
        :return: A Pager with the chapters.
        :rtype: Pager[Chapter]
        """
        params = {}
        if languages:
            params["locales"] = languages
        if created_after:
            params["createdAtSince"] = return_date_string(created_after)
        if updated_after:
            params["updatedAtSince"] = return_date_string(updated_after)
        if published_after:
            params["publishAtSince"] = return_date_string(published_after)
        self.client._add_order(params, order)
        self.client.raise_exception_if_not_authenticated("GET", routes["list_feed"])
        return Pager(
            routes["list_feed"].format(id=self.id), Chapter, self.client, params=params, limit=limit, limit_size=500
        )
