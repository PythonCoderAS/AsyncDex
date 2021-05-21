import warnings
from dataclasses import dataclass
from typing import Any, Dict, Optional, TYPE_CHECKING

from .abc import GenericModelList, Model
from .aggregate import MangaAggregate
from .chapter_list import ChapterList
from .custom_list import CustomList
from .mixins import DatetimeMixin
from .tag import Tag
from .title import TitleList
from ..constants import link_name_to_attribute_mapping, routes
from ..enum import ContentRating, Demographic, FollowStatus, MangaStatus
from ..utils import DefaultAttrDict, copy_key_to_attribute

if TYPE_CHECKING:
    from ..client import MangadexClient
    from .author import Author


@dataclass
class MangaLinks:
    """An object representing the various link types for mangas on MangaDex.

    See the `MangaDex API <https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data>` on how to enter
    these values in for new manga.

    .. versionadded:: 0.5
    """

    anilist_id: Optional[str] = None
    """The ID for the entry on Anilist, if it exists."""

    animeplanet_id: Optional[str] = None
    """The ID for the entry on AnimePlanet, if it exists."""

    bookwalker_id: Optional[str] = None
    """The ID for the entry on Bookwalker, if it exists."""

    mangaupdates_id: Optional[str] = None
    """The ID for the entry on MangaUpdates, if it exists."""

    novelupdates_id: Optional[str] = None
    """The ID for the entry on NovelUpdates, if it exists."""

    kitsu_id: Optional[str] = None
    """The ID for the entry on Kitsu, if it exists."""

    amazon_id: Optional[str] = None
    """The ID for the entry on Amazon, if it exists."""

    cdjapan_id: Optional[str] = None
    """The ID for the entry on CDJapan, if it exists."""

    ebookjapan_id: Optional[str] = None
    """The ID for the entry on EbookJapan, if it exists."""

    myanimelist_id: Optional[str] = None
    """The ID for the entry on MyAnimeList, if it exists."""

    raw_url: Optional[str] = None
    """The URL for the official raws of the manga, if it exists."""

    english_translation_url: Optional[str] = None
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

    def parse(self, data: Dict[str, str]):
        """Parse the links dictionary.

        :param data: The data to parse.
        :type data: Dict[str, str]
        """
        for mangadex_name, asyncdex_name in link_name_to_attribute_mapping.items():
            copy_key_to_attribute(data, mangadex_name, self, asyncdex_name)

    def to_dict(self) -> Dict[str, str]:
        """Convert the class's link attributes to a dictionary that can be sent via the MD api.

        :return: A dict suitable for API use.
        :rtype: Dict[str, str]
        """
        d = {}
        for mangadex_name, asyncdex_name in link_name_to_attribute_mapping.items():
            if getattr(self, asyncdex_name):
                d[mangadex_name] = getattr(self, asyncdex_name)
        return d


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

    last_volume: Optional[str]
    """The last volume of the manga. ``None`` if it is not specified or does not exist.
    
    .. versionchanged:: 0.3
        Changed to a string in order to better match the API specification.
    """

    last_chapter: Optional[str]
    """The last chapter of the manga. ``None`` if it is not specified or does not exist.
    
    .. versionchanged:: 0.3
        Changed to a string in order to better match the API specification.
    """

    demographic: Demographic
    """The manga's demographic."""

    status: MangaStatus
    """The manga's status."""

    year: Optional[int]
    """The year the manga started publication. May be ``None`` if publication hasn't started or is unknown."""

    rating: ContentRating
    """The manga's content rating."""

    tags: GenericModelList[Tag]
    """A list of :class:`.Tag` objects that represent the manga's tags. A manga without tags will have an empty list."""

    authors: GenericModelList["Author"]
    """A list of :class:`.Author` objects that represent the manga's authors.
    
    .. seealso:: :attr:`.artists`
    
    .. note::
        In order to efficiently get all authors and artists in one go, use :meth:`.load_authors`.
    """

    artists: GenericModelList["Author"]
    """A list of :class:`.Author` objects that represent the manga's artists.
    
    .. seealso:: :attr:`.authors`
    
    .. note::
        In order to efficiently get all authors and artists in one go, use :meth:`.load_authors`.
    """

    anilist_id: Optional[str]
    """The ID for the entry on Anilist, if it exists.
    
    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    animeplanet_id: Optional[str]
    """The ID for the entry on AnimePlanet, if it exists.
    
    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    bookwalker_id: Optional[str]
    """The ID for the entry on Bookwalker, if it exists.
    
    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    mangaupdates_id: Optional[str]
    """The ID for the entry on MangaUpdates, if it exists.
    
    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    novelupdates_id: Optional[str]
    """The ID for the entry on NovelUpdates, if it exists.
    
    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    kitsu_id: Optional[str]
    """The ID for the entry on Kitsu, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    amazon_id: Optional[str]
    """The ID for the entry on Amazon, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    cdjapan_id: Optional[str]
    """The ID for the entry on CDJapan, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    ebookjapan_id: Optional[str]
    """The ID for the entry on EbookJapan, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    myanimelist_id: Optional[str]
    """The ID for the entry on MyAnimeList, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    raw_url: Optional[str]
    """The URL for the official raws of the manga, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    english_translation_url: Optional[str]
    """The URL for the official English translation of the manga, if it exists.

    .. deprecated:: 0.5
        Use :attr:`.links` instead.
    """

    chapters: ChapterList
    """A :class:`.ChapterList` representing the chapters of the manga.
    
    .. versionadded:: 0.3
    """

    reading_status: Optional[FollowStatus]
    """A value of :class:`.FollowStatus` representing the logged in user's reading status.
    
    .. versionadded:: 0.5
    """

    links: MangaLinks
    """An instance of :class:`.MangaLinks` with the manga's links.
    
    .. versionadded:: 0.5
    """

    @property
    def anilist_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Anilist entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.anilist_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def animeplanet_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's AnimePlanet entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.animeplanet_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def bookwalker_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Bookwalker entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.bookwalker_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def mangaupdates_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's MangaUpdates entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.mangaupdates_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def novelupdates_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's NovelUpdates entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.novelupdates_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def kitsu_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Kitsu entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.kitsu_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def amazon_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's Amazon entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.amazon_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.amazon_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def cdjapan_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's CDJapan entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.cdjapan_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.cdjapan_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def ebookjapan_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's EbookJapan entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        .. note::
            While the MangaDex API currently returns fully formatted URLs for the :attr:`.ebookjapan_id` attribute,
            this may change in the future. This property will always return a fully formatted URL.

        :return: A full URL or None if :attr:`.ebookjapan_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    @property
    def myanimelist_url(self) -> Optional[str]:
        """Returns a formatted url for the manga's MyAnimeList entry if it exists.

        .. deprecated:: 0.5
            Use :attr:`.links` instead.

        :return: A full URL or None if :attr:`.myanimelist_id` is None.
        :rtype: str
        """
        raise Exception("Trigger getattr")

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.tags = GenericModelList()
        self.titles = DefaultAttrDict(default=lambda: TitleList())
        self.descriptions = DefaultAttrDict(default=lambda: None)
        self.chapters = ChapterList(self)
        self.reading_status = None
        self.links = MangaLinks()
        super().__init__(client, id=id, version=version, data=data)

    def _process_titles(self, title_dict: Dict[str, str]):
        for key, value in title_dict.items():
            self.titles[key].append(value)

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            if "title" in attributes and attributes["title"]:
                self._process_titles(attributes["title"])
            if "altTitles" in attributes and attributes["altTitles"]:
                for item in attributes["altTitles"]:
                    self._process_titles(item)
            if "description" in attributes and attributes["description"]:
                for key, value in attributes["description"].items():
                    self.descriptions[key] = value
            copy_key_to_attribute(attributes, "isLocked", self, "locked", default=False)
            copy_key_to_attribute(attributes, "originalLanguage", self, "original_language")
            copy_key_to_attribute(attributes, "lastVolume", self, "last_volume")
            copy_key_to_attribute(attributes, "lastChapter", self, "last_chapter")
            copy_key_to_attribute(
                attributes,
                "publicationDemographic",
                self,
                "demographic",
                transformation=lambda attrib: Demographic(attrib) if attrib else attrib,
            )
            if "status" in attributes and attributes["status"] == "hitaus":
                attributes["status"] = "hiatus"
            copy_key_to_attribute(
                attributes, "status", self, transformation=lambda attrib: MangaStatus(attrib) if attrib else attrib
            )
            copy_key_to_attribute(attributes, "year", self, transformation=lambda num: int(num) if num else num)
            copy_key_to_attribute(
                attributes,
                "contentRating",
                self,
                "rating",
                transformation=lambda attrib: ContentRating(attrib) if attrib else attrib,
            )
            self._process_times(attributes)
            if "tags" in attributes and attributes["tags"]:
                for tag in attributes["tags"]:
                    assert tag["id"], "Tag ID missing"
                    tag_obj = Tag(self.client, data={"result": "ok", "data": tag})
                    cached_tag = self.client.tag_cache.setdefault(tag_obj.id, tag_obj)
                    cached_tag.transfer(tag_obj)
                    self.tags.append(cached_tag)
            if "links" in attributes and attributes["links"]:
                links = attributes["links"]
                self.links.parse(links)
            self._parse_relationships(data)
            self.chapters = ChapterList(self)

    async def fetch(self):
        """Fetch data about the manga. |permission| ``manga.view``

        :raises: :class:`.InvalidID` if a manga with the ID does not exist.
        """
        await self._fetch("manga.view", "manga")

    async def load_authors(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_authors` with the authors and artists that belong
        to the
        manga.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_authors(*manga.authors, *manga.artists)
        """
        await self.client.batch_authors(*self.authors, *self.artists)

    async def aggregate(self) -> MangaAggregate:
        """Get the aggregate of this manga.

        :return: The manga's aggregate.
        :rtype: MangaAggregate
        """
        r = await self.client.request("GET", routes["aggregate"].format(id=self.id))
        self._check_404(r)
        ma = MangaAggregate()
        ma.parse(await r.json())
        r.close()
        return ma

    async def get_reading_status(self):
        """Gets the manga's reading status. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("GET", routes["manga_read_status"])
        r = await self.client.request("GET", routes["manga_read_status"].format(id=self.id))
        json = await r.json()
        r.close()
        self.reading_status = FollowStatus(json["status"]) if json["status"] else None

    async def set_reading_status(self, status: Optional[FollowStatus]):
        """Sets the manga's reading status. |auth|

        .. versionadded:: 0.5

        :param status: The new status to set. Can be None to remove reading status.
        :type status: Optional[FollowStatus]
        """
        self.client.raise_exception_if_not_authenticated("GET", routes["manga_read_status"])
        r = await self.client.request(
            "POST", routes["manga_read_status"].format(id=self.id), json={"status": status.value if status else None}
        )
        r.close()
        self.reading_status = status

    def __getattr__(self, item: str) -> Any:
        """Used to pass attributes from :attr:`.links` over.

        .. deprecated:: 0.5
            This method will be removed along with all other deprecated attributes and property, and this method
            serves as a way to not break backwards compatibility.

        :param item: The name of the item.
        :type item: str
        :return: The item's value if it exists.
        :rtype: Any
        """
        if not item.startswith("_") and item in self.links.__dict__:
            warnings.warn(
                f"manga.{item} is deprecated. Use manga.links.{item} instead.",
                category=DeprecationWarning,
                stacklevel=3,
            )
            return getattr(self.links, item)
        return object.__getattribute__(self, item)

    async def update(self, notes: Optional[str]):
        """Update the manga using values from the class. |auth|

        .. versionadded:: 0.5

        .. admonition:: Updating manga:

            To update the manga, just set attributes to the values you want to be updated.

            .. warning::
                When updating the titles, use :meth:`list.append` and :meth:`list.extend` instead of assigning a list
                directly.

            Example:

            .. code-block:: python

                manga.titles.en.append("Another english title")
                manga.titles.es.extend(["Spanish title", "Alternate spanish title"]) # Using list.extend
                manga.descriptions.en = "English description"
                manga.last_volume = "2"
                manga.authors = await client.get_authors(name="Author name").as_list()
                manga.year = 2021
                await manga.update("Added some detailed information about the manga")

        :param notes: Optional notes to show to moderators
        :type notes: str
        """
        if not hasattr(self, "titles"):
            await self.fetch()
        title = {}
        alt_titles = []
        for lang, titles in self.titles.items():
            if titles:
                primary, alternates = titles.parts()
                title[lang] = primary
                for item in alternates:
                    alt_titles.append({lang: item})
        if not title:
            raise ValueError("A title needs to be specified.")
        params = {
            "title": title,
            "lastVolume": self.last_volume,
            "lastChapter": self.last_chapter,
            "publicationDemographic": self.demographic.value if self.demographic else None,
            "status": self.status.value if self.status else None,
            "contentRating": self.rating.value if self.rating else None,
            "modNotes": notes,
            "version": self.version,
        }
        if alt_titles:
            params["altTitles"] = alt_titles
        if self.descriptions:
            params["description"] = {k: v for k, v in self.descriptions.items() if v}
        if hasattr(self, "authors") and self.authors:
            params["authors"] = [str(item) for item in self.authors]
        if hasattr(self, "artists") and self.artists:
            params["artists"] = [str(item) for item in self.artists]
        if self.links.to_dict():
            params["links"] = self.links.to_dict()
        if self.original_language:
            params["originalLanguage"] = self.original_language
        if self.year:
            params["year"] = self.year
        self.client.raise_exception_if_not_authenticated("PUT", routes["manga"])
        r = await self.client.request("PUT", routes["manga"].format(id=self.id), json=params)
        json = await r.json()
        r.close()
        manga_obj = type(self)(self.client, data=json)
        self.transfer(manga_obj)

    async def delete(self):
        """Delete the manga. |auth|

        .. versionadded:: 0.5
        """
        return await self._delete("manga")

    async def add_to_list(self, custom_list: CustomList):
        """Add the manga to the custom list. |auth|

        .. versionadded:: 0.5

        :param custom_list: The list to add to.
        :type custom_list: CustomList
        """
        self.client.raise_exception_if_not_authenticated("POST", routes["manga_list"])
        (await self.client.request("POST", routes["manga_list"].format(id=self.id, listId=custom_list.id))).close()
        if self not in custom_list.mangas:
            custom_list.mangas.append(self)

    async def remove_from_list(self, custom_list: CustomList):
        """Remove the manga from the custom list. |auth|

        .. versionadded:: 0.5

        :param custom_list: The list to remove from.
        :type custom_list: CustomList
        """
        self.client.raise_exception_if_not_authenticated("DELETE", routes["manga_list"])
        (await self.client.request("DELETE", routes["manga_list"].format(id=self.id, listId=custom_list.id))).close()
        if self in custom_list.mangas:
            custom_list.mangas.remove(self)

    async def follow(self):
        """Follow the manga. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("POST", routes["manga_follow"])
        (await self.client.request("POST", routes["manga_follow"].format(id=self.id))).close()

    async def unfollow(self):
        """Unfollow the manga. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("DELETE", routes["manga_follow"])
        (await self.client.request("DELETE", routes["manga_follow"].format(id=self.id))).close()
