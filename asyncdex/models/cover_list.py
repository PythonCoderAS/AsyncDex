from typing import Iterable, Optional, TYPE_CHECKING

from .abc import ModelList
from .cover_art import CoverArt

if TYPE_CHECKING:
    from .manga import Manga


class CoverList(ModelList[CoverArt]):
    """An object representing a list of covers from a manga.

    .. versionadded:: 1.0

    :param entries: Pre-fill the CoverList with the given entries.
    :type entries: Iterable[CoverArt]
    """

    manga: "Manga"
    """The :class:`.Manga` that this covers list belongs to."""

    def __init__(self, manga: "Manga", *, entries: Optional[Iterable[CoverArt]] = None):
        super().__init__(entries or [])
        self.manga = manga

    async def get(self):
        """Get the covers for the manga."""
        self.clear()
        async for item in self.manga.client.get_covers(mangas=[self.manga]):
            item.manga = self.manga
            self.append(item)
