from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .abc import GenericModelList, Model
from .pager import Pager
from .manga import Manga
from ..constants import routes
from ..exceptions import PermissionMismatch
from ..list_orders import MangaFeedListOrder
from ..utils import copy_key_to_attribute, return_date_string
from .user import User
from .chapter import Chapter

class ClientUser(User):
    """A :class:`.User` representing the user of the client.

    .. note::
        This is not fully equivalent to a real user. If a client is unauthorized, then the client user object will
        not have a valid UUID.

    .. versionadded:: 0.5
    """

    roles: List[str]
    """The roles of the client user."""

    permissions: List[str]
    """The permissions of the client user."""

    def __init__(self, client: "MangadexClient", *, version: int = 0,
                 data: Optional[Dict[str, Any]] = None):
        super().__init__(client, id="client-user", version=version, data=data)
        self.roles = []
        self.permissions = [
            "manga.view",
            "chapter.view",
            "author.view",
            "scanlation_group.view",
            "manga.list",
            "chapter.list",
            "author.list",
            "scanlation_group.list"
        ]  # These are the default perms for non-authenticated people.

    def permission_check(self, permission_name: str) -> bool:
        """Check if the client user has the given permission.

        :param permission_name: The permission's name.
        :type permission_name: str
        :return: Whether or not the client user has the permission.
        :rtype: bool
        """
        return permission_name in self.permissions

    def permission_exception(self, permission_name: str, method: str, path: str):
        """Check if the client user has the given permission, otherwise throws an exception.

        :param permission_name: The permission's name.
        :type permission_name: str
        :param method: The method to show.

            .. seealso:: :attr:`.Unauthorized.method`.

        :type method: str
        :param path: The path to display.

            .. seealso:: :attr:`.Unauthorized.path`.

        :type path: str
        :raises: :class:`.PermissionMismatch` if the permission does not exist.
        """
        if not self.permission_check(permission_name):
            raise PermissionMismatch(permission_name, method, path, None)

    async def fetch(self):
        r = await self.client.request("GET", routes["auth_check"])
        r.raise_for_status()
        json = await r.json()
        r.close()
        self.roles = json["roles"]
        self.permissions = json["permissions"]
        if not self.client.anonymous_mode:
            await self.fetch_user()

    async def fetch_user(self):
        """Fetch data about the client user from MangaDex servers. This will get the user's UUID."""
        self.client.raise_exception_if_not_authenticated("GET", routes["logged_in_user"])
        r = await self.client.request("GET", routes["logged_in_user"])
        r.raise_for_status()
        json = await r.json()
        r.close()
        self.parse(data=json)

    async def manga_chapters(self, *, languages: Optional[List[str]] = None, created_after: Optional[datetime] =
    None,
                             updated_after: Optional[datetime] = None,
                             published_after: Optional[datetime] = None,
                             order: Optional[MangaFeedListOrder] = None,
                             limit: Optional[int] = None,
                             ) -> Pager[Chapter]:
        """Get the chapters from the manga that the logged in user is following. Requires authentication.

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
        :raise: :class:`.Unauthorized` is there is no authentication.
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
        self.client.raise_exception_if_not_authenticated("GET", routes["logged_user_manga_chapters"])
        return Pager(routes["logged_user_manga_chapters"], Chapter, self.client, params=params, limit=limit,
                     limit_size=500)

    async def manga(self) -> Pager[Manga]:
        """Get the manga that the logged in user follows.

        .. versionadded:: 0.5

        :return: The manga that the logged in user follows.
        :rtype: Pager[Manga]
        """
        self.client.raise_exception_if_not_authenticated("GET", routes["logged_user_manga"])
        return Pager(routes["logged_user_manga"], Manga, self.client)

    def __repr__(self) -> str:
        """Returns a string version of the model useful for development."""
        return f"{type(self).__name__}(roles={self.roles!r}, permissions={self.permissions!r})"
