from typing import Any, Dict, TYPE_CHECKING

from .abc import GenericModelList, Model
from .mixins import DatetimeMixin
from .user import User
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
        """Shortcut method that calls :meth:`.Client.batch_chapters` with the chapters that belong to the group.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_chapters(*user.chapters)
        """
        await self.client.batch_chapters(*self.chapters)

    async def fetch(self):
        await self._fetch("scanlation_group.view", "group")
