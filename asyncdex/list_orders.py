"""Contains the order objects for all the lists."""
from dataclasses import dataclass
from typing import Optional

from .enum import OrderDirection


@dataclass(frozen=True)
class AuthorListOrder:
    """An object representing the various options for ordering a author list returned from
    :meth:`.Client.get_authors`.

    .. versionadded:: 0.4
    """

    name: Optional[OrderDirection] = None
    """The name of an author."""


@dataclass(frozen=True)
class ChapterListOrder:
    """An object representing the various options for ordering a chapter list returned from
    :meth:`.Client.get_chapters`.

    .. versionadded:: 0.4
    """

    creation_time: Optional[OrderDirection] = None
    """The time a chapter was created."""

    update_time: Optional[OrderDirection] = None
    """The time a chapter was updated."""

    publish_time: Optional[OrderDirection] = None
    """The time a chapter was published."""

    # Undocumented in the official docs, see
    # https://discord.com/channels/403905762268545024/839817812012826644/843097446384533544
    title: Optional[OrderDirection] = None
    """The title of the chapter [#V506_CHANGELOG]_."""

    volume: Optional[OrderDirection] = None
    """The chapter's volume."""

    number: Optional[OrderDirection] = None
    """The chapter's number."""


@dataclass(frozen=True)
class GroupListOrder:
    name: Optional[OrderDirection] = None
    """The name of the scanlation group [#V506_CHANGELOG]_."""


@dataclass(frozen=True)
class MangaListOrder:
    """An object representing the various options for ordering a manga list returned from
    :meth:`.Client.search`.

    .. versionadded:: 0.4
    """

    creation_time: Optional[OrderDirection] = None
    """The time a manga was created."""

    update_time: Optional[OrderDirection] = None
    """The time a manga was updated."""

    titles: Optional[OrderDirection] = None
    """The titles of a manga [#V506_CHANGELOG]_."""

    year: Optional[OrderDirection] = None
    """The year a manga was published.
    
    .. seealso:: :attr:`.Manga.year`
    """
