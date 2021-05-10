from typing import Any, Dict, Optional, TYPE_CHECKING

from .abc import Model
from ..utils import DefaultAttrDict

if TYPE_CHECKING:
    from ..client import MangadexClient


class Tag(Model):
    """A :class:`.Model` representing a tag in a Manga.

    .. versionadded:: 0.2
    """

    names: DefaultAttrDict[Optional[str]]
    """A :class:`.DefaultAttrDict` holding the names of the tag.
    
    .. note::
        If a language is missing a name, ``None`` will be returned.
    """

    """The version of the tag. Can be used to cache tag objects."""

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.names = DefaultAttrDict(default=lambda: None)
        super().__init__(client, id=id, version=version, data=data)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            if "name" in attributes:
                for key, value in attributes["name"].items():
                    self.names[key] = value
        self._parse_relationships(data)

    async def fetch(self):
        await self.client.refresh_tag_cache()
