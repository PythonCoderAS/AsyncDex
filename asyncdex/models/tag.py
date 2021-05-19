from collections import defaultdict
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .abc import GenericModelList, Model
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

    descriptions: DefaultAttrDict[Optional[str]]
    """A :class:`.DefaultAttrDict` holding the descriptions of the tag.
    
    .. versionadded:: 0.4
    
    .. note::
        If a language is missing a description, ``None`` will be returned.
    """

    group: Optional[str]
    """The group that the tag belongs to.
    
    .. versionadded:: 0.4
    """

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.names = DefaultAttrDict(default=lambda: None)
        self.descriptions = DefaultAttrDict(default=lambda: None)
        super().__init__(client, id=id, version=version, data=data)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            if "name" in attributes and attributes["name"]:
                for key, value in attributes["name"].items():
                    self.names[key] = value
        self._parse_relationships(data)

    async def fetch(self):
        await self.client.refresh_tag_cache()


class TagDict(Dict[str, Tag]):
    """An object representing a dictionary of tag UUIDs to tag objects.

    .. versionadded:: 0.4
    """

    def groups(self) -> Dict[str, GenericModelList[Tag]]:
        """Categorizes the tags contained into a dictionary of the groups the tags belong to.

        :return: A dictionary of group name to the list of tags that contain the name.
        :rtype: Dict[str, List[Tag]]
        """
        retval = defaultdict(GenericModelList)
        for item in self.values():
            retval[item.group].append(item)
        return dict(retval)

    def __repr__(self) -> str:
        """Provide a string representation of the object.

        .. versionadded:: 0.5

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}{super().__repr__()}"
