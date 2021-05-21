from typing import Any, Dict, TYPE_CHECKING

from .abc import GenericModelList, Model
from .mixins import DatetimeMixin
from .user import User
from ..constants import routes
from ..utils import copy_key_to_attribute

if TYPE_CHECKING:
    from .chapter import Chapter


class Group(Model, DatetimeMixin):
    """A :class:`.Model` representing an individual scanlation group.

    .. versionadded:: 0.3
    """

    name: str
    """The name of the group."""

    leader: User
    """The user who created the group."""

    members: GenericModelList[User]
    """Users who are members of the group."""

    chapters: GenericModelList["Chapter"]
    """A list of chapters uploaded by the group."""

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "name", self)
            copy_key_to_attribute(
                attributes, "leader", self, transformation=lambda attrib: User(self.client, data=attrib)
            )
            if "members" in attributes and attributes["members"]:
                self.members = GenericModelList(User(self.client, data=member) for member in attributes["members"])
            self._process_times(attributes)
        self._parse_relationships(data)
        if hasattr(self, "users"):
            del self.users
        if not hasattr(self, "chapters"):
            self.chapters = GenericModelList()

    async def load_chapters(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_chapters` with the chapters that belong to the group.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_chapters(*user.chapters)
        """
        await self.client.batch_chapters(*self.chapters)

    async def fetch(self):
        """Fetch data about the group. |permission| ``group.view``

        :raises: :class:`.InvalidID` if a group with the ID does not exist.
        """
        await self._fetch("scanlation_group.view", "group")

    async def update(self):
        """Update the scanlation group. |auth|

        .. versionadded:: 0.5
        """
        params = {"name": self.name, "members": [item.id for item in self.members], "leader": self.leader.id}
        self.client.raise_exception_if_not_authenticated("PUT", routes["group"])
        r = await self.client.request("PUT", routes["group"].format(id=self.id), json=params)
        json = await r.json()
        r.close()
        obj = type(self)(self.client, data=json)
        self.transfer(obj)

    async def delete(self):
        """Delete the scanlation group. |auth|

        .. versionadded:: 0.5
        """
        return await self._delete("group")

    async def follow(self):
        """Follow the scanlation group. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("POST", routes["group_follow"])
        (await self.client.request("POST", routes["group_follow"].format(id=self.id))).close()

    async def unfollow(self):
        """Unfollow the scanlation group. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("DELETE", routes["group_follow"])
        (await self.client.request("DELETE", routes["group_follow"].format(id=self.id))).close()
