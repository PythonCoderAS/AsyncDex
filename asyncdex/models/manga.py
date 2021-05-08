from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .abc import Model
from .author import Author
from .mixins import DatetimeMixin
from .tag import Tag
from .title import TitleList
from ..enum import ContentRating, Demographic, MangaStatus
from ..utils import DefaultAttrDict, copy_key_to_attribute

if TYPE_CHECKING:
    from ..client import MangadexClient


class Manga(Model, DatetimeMixin):
    """A :class:`.Model` representing an individual manga.

    .. versionadded:: 0.2
    """

    titles: DefaultAttrDict[TitleList]
    """A :class:`.DefaultAttrDict` holding the titles of the manga."""

    descriptions: DefaultAttrDict[Optional[str]]
    """A :class:`.DefaultAttrDict` holding the descriptions of the manga.
    
    .. note::
        If a language is missing a description, ``None`` will be returned.
    """

    original_language: str
    """The original language that the manga was released in."""

    locked: bool
    """A locked manga. Usually means that chapter details cannot be modified."""

    last_volume: Optional[int]
    """The last volume of the manga. ``None`` if it is not specified or does not exist."""

    last_chapter: Optional[int]
    """The last chapter of the manga. ``None`` if it is not specified or does not exist."""

    demographic: Demographic
    """The manga's demographic."""

    status: MangaStatus
    """The manga's status."""

    year: Optional[int]
    """The year the manga started publication. May be ``None`` if publication hasn't started or is unknown."""

    rating: ContentRating
    """The manga's content rating."""

    tags: List[Tag]
    """A list of :class:`.Tag` objects that represent the manga's tags. A manga without tags will have an empty list."""

    authors: List[Author]
    """A list of :class:`.Author` objects that represent the manga's authors.
    
    .. seealso:: :attr:`.artists`
    
    .. note::
        In order to efficiently get all authors and artists in one go, use :meth:`.load_authors`.
    """

    artists: List[Author]
    """A list of :class:`.Author` objects that represent the manga's artists.
    
    .. seealso:: :attr:`.authors`
    
    .. note::
        In order to efficiently get all authors and artists in one go, use :meth:`.load_authors`.
    """

    anilist_id: Optional[str]
    """The ID for the entry on Anilist, if it exists."""

    animeplanet_id: Optional[str]
    """The ID for the entry on AnimePlanet, if it exists."""

    bookwalker_id: Optional[str]
    """The ID for the entry on Bookwalker, if it exists."""

    mangaupdates_id: Optional[str]
    """The ID for the entry on MangaUpdates, if it exists."""

    novelupdates_id: Optional[str]
    """The ID for the entry on NovelUpdates, if it exists."""

    kitsu_id: Optional[str]
    """The ID for the entry on Kitsu, if it exists."""

    amazon_id: Optional[str]
    """The ID for the entry on Amazon, if it exists."""

    cdjapan_id: Optional[str]
    """The ID for the entry on CDJapan, if it exists."""

    ebookjapan_id: Optional[str]
    """The ID for the entry on EbookJapan, if it exists."""

    myanimelist_id: Optional[str]
    """The ID for the entry on MyAnimeList, if it exists."""

    raw_url: Optional[str]
    """The URL for the official raws of the manga, if it exists."""

    english_translation_url: Optional[str]
    """The URL for the official English translation of the manga, if it exists."""

    @property
    def anilist_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Anilist entry if it exists.

        :return: A full URL or None if :attr:`.anilist_id` is None.
        :rtype: str
        """
        return self.anilist_id and f"https://anilist.co/manga/{self.anilist_id}"

    @property
    def animeplanet_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's AnimePlanet entry if it exists.

        :return: A full URL or None if :attr:`.animeplanet_id` is None.
        :rtype: str
        """
        return self.animeplanet_id and f"https://www.anime-planet.com/manga/{self.animeplanet_id}"

    @property
    def bookwalker_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Bookwalker entry if it exists.

        :return: A full URL or None if :attr:`.bookwalker_id` is None.
        :rtype: str
        """
        return self.bookwalker_id and f"https://bookwalker.jp/{self.bookwalker_id}"

    @property
    def mangaupdates_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's MangaUpdates entry if it exists.

        :return: A full URL or None if :attr:`.mangaupdates_id` is None.
        :rtype: str
        """
        return self.mangaupdates_id and f"https://www.mangaupdates.com/series.html?id={self.mangaupdates_id}"

    @property
    def novelupdates_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's NovelUpdates entry if it exists.

        :return: A full URL or None if :attr:`.novelupdates_id` is None.
        :rtype: str
        """
        return self.novelupdates_id and f"https://www.novelupdates.com/series/{self.novelupdates_id}"

    @property
    def kitsu_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Kitsu entry if it exists.

        :return: A full URL or None if :attr:`.kitsu_id` is None.
        :rtype: str
        """
        return self.kitsu_id and f"https://kitsu.io/manga/{self.kitsu_id}"

    @property
    def amazon_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Amazon entry if it exists.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.amazon_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.amazon_id` is None.
        :rtype: str
        """
        return self.amazon_id

    @property
    def cdjapan_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's CDJapan entry if it exists.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.cdjapan_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.cdjapan_id` is None.
        :rtype: str
        """
        return self.cdjapan_id

    @property
    def ebookjapan_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's EbookJapan entry if it exists.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.ebookjapan_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.ebookjapan_id` is None.
        :rtype: str
        """
        return self.ebookjapan_id

    @property
    def myanimelist_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's MyAnimeList entry if it exists.

        :return: A full URL or None if :attr:`.myanimelist_id` is None.
        :rtype: str
        """
        return self.myanimelist_id and f"https://myanimelist.net/manga/{self.myanimelist_id}"

    def __init__(self, client: "MangadexClient", *, id: Optional[str] = None, version: int = 0,
                 data: Optional[Dict[str, Any]] = None):
        self.tags = []
        self.titles = DefaultAttrDict(default=lambda: TitleList())
        self.descriptions = DefaultAttrDict(default=lambda: None)
        super().__init__(client, id=id, version=version, data=data)

    def _process_titles(self, title_dict: Dict[str, str]):
        for key, value in title_dict.items():
            self.titles[key].append(value)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            if "title" in attributes:
                self._process_titles(attributes["title"])
            if "altTitles" in attributes:
                for item in attributes["altTitles"]:
                    self._process_titles(item)
            if "description" in attributes:
                for key, value in attributes["description"].items():
                    self.descriptions[key] = value
            copy_key_to_attribute(attributes, "isLocked", self, "locked", default=False)
            copy_key_to_attribute(attributes, "originalLanguage", self, "original_language")
            copy_key_to_attribute(attributes, "lastVolume", self, "last_volume",
                                  transformation=lambda num: int(num) if num else num)
            copy_key_to_attribute(attributes, "lastChapter", self, "last_chapter",
                                  transformation=lambda num: int(num) if num else num)
            copy_key_to_attribute(attributes, "publicationDemographic", self, "demographic",
                                  transformation=lambda attrib: Demographic(attrib) if attrib else attrib)
            copy_key_to_attribute(attributes, "status", self,
                                  transformation=lambda attrib: MangaStatus(attrib) if attrib else attrib)
            copy_key_to_attribute(attributes, "year", self,
                                  transformation=lambda num: int(num) if num else num)
            copy_key_to_attribute(attributes, "contentRating", self, "rating",
                                  transformation=lambda attrib: ContentRating(attrib) if attrib else attrib)
            self._process_times(attributes)
            if "tags" in attributes:
                for tag in attributes["tags"]:
                    assert tag["id"], "Tag ID missing"
                    tag_obj = Tag(self.client, data={"result": "ok", "data": tag})
                    cached_tag = self.client.tag_cache.setdefault(tag_obj.id, tag_obj)
                    cached_tag.transfer(tag_obj)
                    self.tags.append(cached_tag)
            if "links" in attributes and attributes["links"]:
                links = attributes["links"]
                copy_key_to_attribute(links, "al", self, "anilist_id")
                copy_key_to_attribute(links, "ap", self, "animeplanet_id")
                copy_key_to_attribute(links, "bw", self, "bookwalker_id")
                copy_key_to_attribute(links, "mu", self, "mangaupdates_id")
                copy_key_to_attribute(links, "nu", self, "novelupdates_id")
                copy_key_to_attribute(links, "kt", self, "kitsu_id")
                copy_key_to_attribute(links, "amz", self, "amazon_id")
                copy_key_to_attribute(links, "cdj", self, "cdjapan_id")
                copy_key_to_attribute(links, "ebj", self, "ebookjapan_id")
                copy_key_to_attribute(links, "mal", self, "myanimelist_id")
                copy_key_to_attribute(links, "raw", self, "raw_url")
                copy_key_to_attribute(links, "engtl", self, "english_translation_url")
            self._parse_relationships(data)

    async def fetch(self):
        await self._fetch("manga")

    async def load_authors(self):
        """Shortcut method that calls :meth:`.Client.batch_authors` with the authors and artists that belong to the
        manga.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_authors(*manga.authors, *manga.artists)
        """
        await self.client.batch_authors(*self.authors, *self.artists)
