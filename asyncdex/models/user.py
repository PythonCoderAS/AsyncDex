from typing import Any, Dict, TYPE_CHECKING

from .abc import GenericModelList, Model
from ..utils import copy_key_to_attribute

if TYPE_CHECKING:
    from .chapter import Chapter


class User(Model):
    """A :class:`.Model` representing an individual user.

    .. versionadded:: 0.3
    """

    username: str
    """THe user's username."""

    chapters: GenericModelList["Chapter"]
    """The chapters the user uploaded"""

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "id" in data:
            self.id = data["id"]
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "username", self)
        self._parse_relationships(data)
        if not hasattr(self, "chapters"):
            self.chapters = GenericModelList()

    async def load_chapters(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_chapters` with the chapters that belong to the user.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_chapters(*user.chapters)
        """
        await self.client.batch_chapters(*self.chapters)

    async def fetch(self):
        await self._fetch(None, "user")
