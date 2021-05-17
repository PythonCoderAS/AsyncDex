import asyncio
import re
import warnings
from collections import defaultdict
from datetime import datetime
from os import makedirs
from os.path import exists, join
from typing import Any, Callable, Dict, Iterable, List, Optional, TYPE_CHECKING, Tuple

from aiohttp import ClientError
from natsort import natsort_keygen

from .abc import Model
from .aggregate import MangaAggregate, VolumeAggregate
from .group import Group
from .mixins import DatetimeMixin
from .pager import Pager
from .user import User
from ..constants import invalid_folder_name_regex, routes
from ..enum import DuplicateResolutionAlgorithm
from ..utils import InclusionExclusionPair, Interval, copy_key_to_attribute, return_date_string

if TYPE_CHECKING:
    from .manga import Manga


class Chapter(Model, DatetimeMixin):
    """A :class:`.Model` representing an individual chapter.

    .. versionadded:: 0.3
    """

    volume: Optional[str]
    """The volume of the chapter. ``None`` if the chapter belongs to no volumes."""

    number: Optional[str]
    """The number of the chapter. ``None`` if the chapter is un-numbered (such as in an anthology).
    
    .. note::
        A chapter can have a number, a title, or both. If a chapter's number is ``None``, it must have a title. 
    """

    title: Optional[str]
    """The title of the chapter. ``None`` if the chapter does not have a title.
    
    .. note::
        A chapter can have a number, a title, or both. If a chapter's title is ``None``, it must have a number.
    """

    language: str
    """The language of the chapter."""

    hash: str
    """The chapter's hash."""

    page_names: List[str]
    """A list of strings containing the filenames of the pages.
    
    .. seealso:: :attr:`.data_saver_page_names`
    """

    data_saver_page_names: List[str]
    """A list of strings containing the filenames of the data saver pages.
    
    .. seealso:: :attr:`.page_names`
    """

    publish_time: datetime
    """A :class:`datetime.datetime` representing the time the chapter was published.

    .. seealso:: :attr:`.created_at`

    .. note::
        The datetime is **timezone aware** as it is parsed from an ISO-8601 string.
    """

    manga: "Manga"
    """The manga that this chapter belongs to."""

    user: User
    """The user that uploaded this chapter."""

    groups: List[Group]
    """The groups that uploaded this chapter."""

    @property
    def name(self) -> str:
        """Returns a nicely formatted name based on available fields. Includes the volume number, chapter number,
        and chapter title if any one or more of them exist.

        :return: Formatted name
        :rtype: str
        """
        if self.number:
            constructed = ""
            if self.volume:
                constructed += f"Volume {self.volume} "
            if self.number.isdecimal():
                num_rep = float(self.number)
                if num_rep.is_integer():
                    num_rep = int(num_rep)
            else:
                num_rep = self.number
            constructed += f"Chapter {num_rep}"
            if self.title:
                constructed += f": {self.title}"
            return constructed
        else:
            return self.title

    @property
    def sorting_number(self) -> float:
        """Returns ``0`` if the chapter does not have a number, otherwise returns the chapter's number.

        :return: A number usable for sorting.
        :rtype: float
        """
        return float(self.number) if self.number.isdecimal() else -1

    async def pages(self, *, data_saver: bool = False, ssl_only: bool = False) -> List[str]:
        """Get fully formatted page URLs.

        .. note::
            The given page URLs are only valid for a short timeframe. These URLs cannot be used for hotlinking.

        :param data_saver: Whether or not to return the pages for the data saver URLs. Defaults to ``False``.
        :type data_saver: bool
        :param ssl_only: Whether or not the given URL has port ``443``. Useful if your firewall blocks outbound
            connections to ports that are not port ``443``. Defaults to ``False``.

            .. note::
                This will lower the pool of available clients and can cause higher latencies.

        :type ssl_only: bool
        :return: A list of valid URLs in the order of the pages.
        :rtype: List[str]
        """
        if not hasattr(self, "page_names"):
            await self.fetch()
        r = await self.client.request(
            "GET", routes["md@h"].format(chapterId=self.id), params={"forcePort443": ssl_only}
        )
        base_url = (await r.json())["baseUrl"]
        r.close()
        return [
            f"{base_url}/{'data-saver' if data_saver else 'data'}/{self.hash}/{filename}"
            for filename in (self.data_saver_page_names if data_saver else self.page_names)
        ]

    async def get_page(self, url: str):
        """Alias for :meth:`.MangadexClient.get_page`.

        .. deprecated:: 0.4
        """
        warnings.warn(
            "Chapter.get_page() is deprecated, use MangadexClient.get_page() instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return await self.client.get_page(url)

    async def download_chapter(
        self,
        *,
        folder_format: str = "{manga}/{chapter_num}{separator}{title}",
        file_format: str = "{num}",
        as_bytes_list: bool = False,
        overwrite: bool = True,
        retries: int = 3,
        use_data_saver: bool = False,
        ssl_only: bool = False,
    ) -> Optional[List[bytes]]:
        """Download all of the pages of the chapter and either save them locally to the filesystem or return the raw
        bytes.

        :param folder_format: The format of the folder to create for the chapter. The folder can already be existing.
            The default format is ``{manga}/{chapter_num}{separator}{chapter_title}``.

            .. note::
                Specify ``.`` if you want to save the pages in the current folder.

            Available variables:

            * ``{manga}``: The name of the manga. If the chapter's manga object does not contain a title object,
              it will be fetched.
            * ``{chapter_num}``: The number of the chapter, if it exists.
            * ``{separator}``: A separator if both the chapter's number and title exists.
            * ``{title}``: The title of the chapter, if it exists.

        :type folder_format: str
        :param file_format: The format of the individual image file names. The default format is ``{num}``.

            .. note::
                The file extension is applied automatically from the real file name. There is no need to include it.

            Available variables:

            * ``{num}``: The numbering of the image files starting from 1. This respects the order the images are in
              inside of :attr:`.page_names`.
            * ``{num0}``: The same as ``{num}`` but starting from 0.
            * ``{name}``: The actual filename of the image from :attr:`.page_names`, without the file extension.

        :type file_format: str
        :param as_bytes_list: Whether or not to return the pages as a list of raw bytes. Setting this parameter to
            ``True`` will ignore the value of the ``folder_format`` parameter.
        :type as_bytes_list: bool
        :param overwrite: Whether or not to override existing files with the same name as the page. Defaults to
            ``True``.
        :type overwrite: bool
        :param retries: How many times to retry a chapter if a MD@H node does not let us download the pages.
            Defaults to ``3``.
        :type retries: int
        :param use_data_saver: Whether or not to use the data saver pages or the normal pages. Defaults to ``False``.
        :type use_data_saver: bool
        :param ssl_only: Whether or not the given URL has port ``443``. Useful if your firewall blocks outbound
            connections to ports that are not port ``443``. Defaults to ``False``.

            .. note::
                This will lower the pool of available clients and can cause higher download times.

        :type ssl_only: bool
        :raises: :class:`aiohttp.ClientResponseError` if there is an error after all retries are exhausted.
        :return: A list of byte strings if ``as_bytes_list`` is ``True`` else None.
        :rtype: Optional[List[bytes]]
        """
        if not hasattr(self, "page_names"):
            await self.fetch()
        pages = await self.pages(data_saver=use_data_saver, ssl_only=ssl_only)
        try:
            items = await asyncio.gather(*[self.get_page(url) for url in pages])
        except ClientError:
            if retries > 0:
                return await self.download_chapter(
                    folder_format=folder_format,
                    as_bytes_list=as_bytes_list,
                    overwrite=overwrite,
                    retries=retries - 1,
                    use_data_saver=use_data_saver,
                    ssl_only=ssl_only,
                )
            else:
                raise
        else:
            byte_list = await asyncio.gather(*[item.read() for item in items])
            if as_bytes_list:
                return byte_list  # NOQA: ignore; This is needed because for whatever reason PyCharm cannot guess the
                # output of asyncio.gather()
            else:
                base = ""
                if not as_bytes_list:
                    chapter_num = self.number or ""
                    separator = " - " if self.number and self.title else ""
                    title = (
                        re.sub("_{2,}", "_", invalid_folder_name_regex.sub("_", self.title.strip()))
                        if self.title
                        else ""
                    )
                    # This replaces invalid characters with underscores then deletes duplicate underscores in a
                    # series. This
                    # means that a name of ``ex___ample`` becomes ``ex_ample``.
                    if not self.manga.titles:
                        await self.manga.fetch()
                    manga_title = self.manga.titles[self.language].primary or (
                        self.manga.titles.first().primary if self.manga.titles else self.manga.id
                    )
                    manga_title = re.sub("_{2,}", "_", invalid_folder_name_regex.sub("_", manga_title.strip()))
                    base = folder_format.format(
                        manga=manga_title, chapter_num=chapter_num, separator=separator, title=title
                    )
                    makedirs(base, exist_ok=True)
                for original_file_name, (num, item) in zip(
                    self.data_saver_page_names if use_data_saver else self.page_names, enumerate(byte_list, start=1)
                ):
                    filename = (
                        file_format.format(num=num, num0=num - 1, name=original_file_name)
                        + "."
                        + original_file_name.rpartition(".")[-1]
                    )
                    full_path = join(base, filename)
                    if not (exists(full_path) and overwrite):
                        with open(full_path, "wb") as fp:
                            fp.write(item)

    @staticmethod
    def _get_number_from_chapter_string(chapter_str: str) -> Tuple[Optional[float], Optional[str]]:
        if not chapter_str:
            return None, None
        elif chapter_str.isdecimal():
            return float(chapter_str), None
        else:
            # Unfortunately for us some people decided to enter in garbage data, which means that we cannot cleanly
            # convert to a float. Attempt to try to get something vaguely resembling a number or return a null
            # chapter number and set the title as the value for the chapter number.
            match = re.search(r"[\d.]+", chapter_str)
            return None if not match else float(match.group(0)), chapter_str

    def parse(self, data: Dict[str, Any]):
        super().parse(data)
        if "data" in data and "attributes" in data["data"]:
            attributes = data["data"]["attributes"]
            copy_key_to_attribute(attributes, "volume", self)
            copy_key_to_attribute(attributes, "title", self)
            copy_key_to_attribute(attributes, "chapter", self, "number")
            copy_key_to_attribute(attributes, "translatedLanguage", self, "language")
            copy_key_to_attribute(attributes, "hash", self)
            copy_key_to_attribute(attributes, "data", self, "page_names")
            copy_key_to_attribute(attributes, "dataSaver", self, "data_saver_page_names")
            self._process_times(attributes)
            self._parse_relationships(data)
            if hasattr(self, "_users"):
                self.user = self._users[0]
                del self._users
            if self.mangas:
                # This is needed to move the list of Mangas created by the parse_relationships function into a
                # singular manga, since there can never be >1 manga per chapter.
                self.mangas: List[Manga]
                self.manga = self.mangas[0]
            if hasattr(self, "mangas"):
                del self.mangas

    def _process_times(self, attributes: Dict[str, str]):
        super()._process_times(attributes)
        copy_key_to_attribute(
            attributes,
            "publishAt",
            self,
            "publish_time",
            transformation=lambda attrib: datetime.fromisoformat(attrib) if attrib else attrib,
        )

    async def fetch(self):
        await self._fetch("chapter")

    async def load_groups(self):
        """Shortcut method that calls :meth:`.Client.batch_groups` with the groups that belong to the group.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_groups(*user.groups)
        """
        await self.client.batch_groups(*self.groups)


def _chapter_attr_map(items: List[Chapter], attr: str):
    return {getattr(item, attr): item for item in items}


def _get_smallest_creation_time(items: List[Chapter]):
    return sorted(((item.created_at, item) for item in items), key=lambda i: i[0])[0]


def _check_values(set1: set, set2: set) -> int:
    """This checks how many of the values present inside of the first set are in the second set."""
    match = 0
    if set1.issuperset(set2):
        match += 1
    for item in set2:
        if set1.issuperset({item}):
            match += 1
    return match


def _resolve_duplicates(
    chapter_list: List[Chapter],
    algo: List[DuplicateResolutionAlgorithm],
    specific_groups: Optional[Iterable[Group]],
    specific_users: Optional[Iterable[User]],
):
    """Actually does the duplicate resolving."""
    last_chapter: Optional[set] = None
    specific_groups = specific_groups or []
    specific_users = specific_users or []
    chapter_dict: Dict[Optional[str], List[Chapter]] = defaultdict(list)
    final = ChapterList(chapter_list[0].manga)
    for item in chapter_list:
        chapter_dict[item.number].append(item)
    final.extend(chapter_dict.pop(None, []))
    # We grouped up the chapters by number for logical sorting.
    if DuplicateResolutionAlgorithm.VIEWS_ASC in algo or DuplicateResolutionAlgorithm.VIEWS_DESC in algo:
        raise NotImplementedError("MangaDex API does not return views yet, sorry!")
    duplicate_last_prios = _check_values(
        {
            DuplicateResolutionAlgorithm.VIEWS_ASC,
            DuplicateResolutionAlgorithm.VIEWS_DESC,
            DuplicateResolutionAlgorithm.CREATION_DATE_ASC,
            DuplicateResolutionAlgorithm.CREATION_DATE_DESC,
        },
        set(algo),
    )
    if duplicate_last_prios > 1:
        raise ValueError("The lowest-priority operations cannot be combined.")
    elif not duplicate_last_prios:
        algo.append(DuplicateResolutionAlgorithm.CREATION_DATE_ASC)
    for chapter_num, items in chapter_dict.items():
        # Now the sorting begins.
        matches_found = items
        if last_chapter is not None and DuplicateResolutionAlgorithm.PREVIOUS_GROUP in algo:
            # Determine the priority. Obviously, if the last chapter was made by one group, that's easy. But if
            # multiple groups contributed towards a chapter, we would want to match chapters made by only one of the
            # multiple groups. Use a priority system to determine who gets to move on
            set_group = defaultdict(list)
            for item in matches_found:
                set_match_prio = _check_values(set(item.groups), last_chapter)
                if set_match_prio:
                    set_group[set_match_prio].append(item)
            if set_group:
                matches_found = sorted(set_group.items(), key=lambda item: item[0])[0][1]
        if len(matches_found) > 1 and DuplicateResolutionAlgorithm.SPECIFIC_GROUP in algo:
            # Either we did not go the last time or there were more than one chapter with the same group priority.
            # Now we try if the "Specific Group" strategy was chosen.
            matches = list(filter(lambda chapter: _check_values(set(item.groups), set(specific_groups)), matches_found))
            if len(matches) > 0:
                matches_found = matches
        else:
            final.append(matches_found[0])
            continue
        if len(matches_found) > 1 and DuplicateResolutionAlgorithm.SPECIFIC_USER in algo:
            matches = list(filter(lambda chapter: item.user in specific_users, matches_found))
            if len(matches) > 0:
                matches_found = matches
        else:
            final.append(matches_found[0])
            continue
        if len(matches_found) > 1:
            if DuplicateResolutionAlgorithm.CREATION_DATE_ASC in algo:
                final.append(sorted(matches_found, key=lambda chapter: chapter.created_at)[0])
            elif DuplicateResolutionAlgorithm.CREATION_DATE_DESC in algo:
                final.append(sorted(matches_found, key=lambda chapter: chapter.created_at, reverse=True)[0])
            elif DuplicateResolutionAlgorithm.VIEWS_ASC in algo:
                # final.append(sorted(matches_found, key=lambda chapter: chapter.created_at)[0])
                raise NotImplementedError("DuplicateResolutionAlgorithm.VIEWS_ASC not implemented.")
            elif DuplicateResolutionAlgorithm.VIEWS_DESC in algo:
                # final.append(sorted(matches_found, key=lambda chapter: chapter.created_at)[0])
                raise NotImplementedError("DuplicateResolutionAlgorithm.VIEWS_DESC not implemented.")
        else:
            final.append(matches_found[0])
    return final


class ChapterList(List[Chapter]):
    """An object representing a list of chapters from a manga.

    .. versionadded:: 0.3

    :param entries: Pre-fill the ChapterList with the given entries.
    :type entries: Iterable[Chapter]
    """

    manga: "Manga"
    """The :class:`.Manga` that this chapter list belongs to."""

    def __init__(self, manga: "Manga", *, entries: Optional[Iterable[Chapter]] = None):
        super().__init__(entries or [])
        self.manga = manga

    async def get(
        self,
        *,
        locales: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        published_after: Optional[datetime] = None,
    ):
        """Gets the list of chapters.

        :param locales: The locales to filter by.
        :type locales: List[str]
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
        """
        params = {}
        if locales:
            params["locales"] = locales
        if created_after:
            params["createdAtSince"] = return_date_string(created_after)
        if updated_after:
            params["updatedAtSince"] = return_date_string(updated_after)
        if published_after:
            params["publishAtSince"] = return_date_string(published_after)
        async for item in Pager(
            routes["manga_chapters"].format(id=self.manga.id), Chapter, self.manga.client, params=params, limit_size=500
        ):
            item: Chapter
            item.manga = self.manga
            if item in self:
                self[self.index(item)] = item
            else:
                self.append(item)

    def filter(
        self,
        *,
        locales: Optional[List[str]] = None,
        creation_time: Optional[Interval[datetime]] = None,
        update_time: Optional[Interval[datetime]] = None,
        publish_time: Optional[Interval[datetime]] = None,
        views: Optional[Interval[int]] = None,
        has_number: Optional[bool] = None,
        chapter_number_range: Optional[Interval[float]] = None,
        chapter_numbers: Optional[InclusionExclusionPair[Optional[float]]] = None,
        remove_duplicates: bool = False,
        duplicate_strategy: Optional[List[DuplicateResolutionAlgorithm]] = None,
        duplicate_strategy_groups: Optional[List[Group]] = None,
        duplicate_strategy_users: Optional[List[User]] = None,
        groups: Optional[InclusionExclusionPair[Group]] = None,
        users: Optional[InclusionExclusionPair[User]] = None,
    ) -> "ChapterList":
        """Filter the chapter list and return a new :class:`.ChapterList`. Calling this method without specifying any
        additional filtering mechanisms will return a shallow copy of the list.

        The order of the filter will be as follows:

        #. Filter the datetimes first
        #. Filter by the intervals
        #. Filter by the inclusion and exclusion pairs
        #. Filter duplicates

        :param locales: The locales that should be present in the chapters.
        :type locales: List[str]
        :param creation_time: An :class:`.Interval` representing the bounds of the chapter's creation time.
            :attr:`.Interval.min` will select all chapters created **after** the given time, and :attr:`.Interval.max`
            will select all chapters created **before** the given time.

            .. note::
                The datetime objects needs to be a non-timezone aware datetime in UTC time. A datetime in any
                timezone can be converted to a naive UTC timezone by:

                .. code-block:: python

                    from datetime import timezone
                    # dt is the datetime object.
                    utc_naive = dt.astimezone(timezone.utc).replace(tzinfo=None)

            Example intervals:

            .. code-block:: python

                from asyncdex import Interval
                min_interval = Interval(min=datetime.datetime(2021, 1, 1))
                max_interval = Interval(max=datetime.datetime(2021, 1, 1))
                both = Interval(datetime.datetime(2021, 1, 1), datetime.datetime(2021, 5, 1))

        :type creation_time: Interval[datetime]
        :param update_time: An :class:`.Interval` representing the bounds of the chapter's update time.
            :attr:`.Interval.min` will select all chapters updated **after** the given time, and :attr:`.Interval.max`
            will select all chapters updated **before** the given time.

            .. note::
                The datetime objects needs to be a non-timezone aware datetime in UTC time. A datetime in any
                timezone can be converted to a naive UTC timezone by:

                .. code-block:: python

                    from datetime import timezone
                    # dt is the datetime object.
                    utc_naive = dt.astimezone(timezone.utc).replace(tzinfo=None)

            Example intervals:

            .. code-block:: python

                from asyncdex import Interval
                min_interval = Interval(min=datetime.datetime(2021, 1, 1))
                max_interval = Interval(max=datetime.datetime(2021, 1, 1))
                both = Interval(datetime.datetime(2021, 1, 1), datetime.datetime(2021, 5, 1))

        :type update_time: Interval[datetime]
        :param publish_time: An :class:`.Interval` representing the bounds of the chapter's publish time.
            :attr:`.Interval.min` will select all chapters published **after** the given time, and :attr:`.Interval.max`
            will select all chapters published **before** the given time.

            .. note::
                The datetime objects needs to be a non-timezone aware datetime in UTC time. A datetime in any
                timezone can be converted to a naive UTC timezone by:

                .. code-block:: python

                    from datetime import timezone
                    # dt is the datetime object.
                    utc_naive = dt.astimezone(timezone.utc).replace(tzinfo=None)

            Example intervals:

            .. code-block:: python

                min_interval = Interval(min=datetime.datetime(2021, 1, 1))
                max_interval = Interval(max=datetime.datetime(2021, 1, 1))
                both = Interval(datetime.datetime(2021, 1, 1), datetime.datetime(2021, 5, 1))

        :type publish_time: Interval[datetime]
        :param views: An :class:`.Interval` of the views that a manga can have.

            .. warning::
                The mangadex API does not return views yet, so specifying something for this parameter will result in
                :class:`.NotImplementedError` being raised.

            Example intervals:

            .. code-block:: python

                from asyncdex import Interval
                min_interval = Interval(min=100)
                max_interval = Interval(max=25000)
                both = Interval(100, 25000)

        :type views: Interval[int]
        :param has_number: Only select chapters with valid numbers.
        :type has_number: bool
        :param chapter_number_range: An :class:`.Interval` of the number of the chapter.

            .. note::
                Chapters without a number will be given a provisional number of 0 when sorted.

            Example intervals:

            .. code-block:: python

                from asyncdex import Interval
                min_interval = Interval(min=2)
                max_interval = Interval(max=20.5)
                both = Interval(2, 20.5)

        :type chapter_number_range: Interval[float]
        :param chapter_numbers: An :class:`.InclusionExclusionPair` denoting the chapter numbers that are either
            included or excluded.

            .. note::
                Chapters without a number will be given a provisional number of 0 when sorted.

            Example inclusion/exclusion pairs:

            .. code-block:: python

                from asyncdex import InclusionExclusionPair
                include = InclusionExclusionPair(include=[5, 6])
                excluse = InclusionExclusionPair(exclude=[7, 8, 9.5])

        :type chapter_numbers: InclusionExclusionPair[float]
        :param remove_duplicates: Whether or not to remove duplicate chapters, ie chapters with the same chapter number.

            .. note::
                This will not take locales into consideration. Make sure to specify a locale in the ``locales``
                parameter if you want duplicates filtered for a specific locale.

        :type remove_duplicates: bool
        :param duplicate_strategy: The list of strategies used to resolve duplicates. See the values in
            :class:`.DuplicateResolutionAlgorithm` to find the possible algorithms. By default, the strategy of
            choosing the previous group and the strategy of choosing the first chapter chronologically when there is
            no previous group will be used.

            .. note::
                If an adequate strategy is not found for dealing with certain chapters, the fallback mechanism of
                selecting the chapter that was created first will be used.

        :type duplicate_strategy: List[DuplicateResolutionAlgorithm]
        :param duplicate_strategy_groups: The groups to use for :attr:`.DuplicateResolutionAlgorithm.SPECIFIC_GROUP`.

            .. note::
                If the group is not present in all the chapters for a specific number, an alternate resolution
                algorithm will be used. Use the ``include_groups`` param if you only want chapters from that group.

        :type duplicate_strategy_groups: List[Group]
        :param duplicate_strategy_users: The users to use for :attr:`.DuplicateResolutionAlgorithm.SPECIFIC_USER`.

            .. note::
                If the user is not present in all the chapters for a specific number, an alternate resolution
                algorithm will be used. Use the ``include_users`` param if you only want chapters from that user.

        :type duplicate_strategy_users: List[User]
        :param users: An :class:`.InclusionExclusionPair` denoting the users to include/exclude from the listing.
        :type users: InclusionExclusionPair[User]
        :param groups: An :class:`.InclusionExclusionPair` denoting the groups to include/exclude from the listing.
        :type groups: InclusionExclusionPair[Group]
        :return: A filtered :class:`.ChapterList`.

            .. note::
                The filtered list is not cached in :attr:`.Manga.chapters`.

        :rtype: ChapterList
        """
        base: Iterable[Chapter] = self.copy()
        options = (
            locales,
            creation_time,
            update_time,
            publish_time,
            views,
            has_number,
            chapter_number_range,
            chapter_numbers,
            duplicate_strategy,
            duplicate_strategy_groups,
            duplicate_strategy_users,
            groups,
            users,
        )
        if options.count(None) == len(options) and not remove_duplicates:
            return ChapterList(self.manga, entries=self.copy())
        duplicate_strategy = duplicate_strategy or [
            DuplicateResolutionAlgorithm.PREVIOUS_GROUP,
            DuplicateResolutionAlgorithm.CREATION_DATE_ASC,
        ]
        if locales:
            base = filter(lambda chapter: chapter.language in locales, base)
        if has_number:
            base = filter(lambda chapter: chapter.number is not None, base)
        if creation_time:
            base = filter(lambda chapter: chapter.created_at in creation_time, base)
        if update_time:
            base = filter(lambda chapter: chapter.created_at in update_time, base)
        if publish_time:
            base = filter(lambda chapter: chapter.created_at in publish_time, base)
        if views:
            raise NotImplementedError("Views not implemented in the MangaDex API.")
            # base = filter(lambda chapter: chapter.views in views, base)
        if chapter_number_range:
            base = filter(lambda chapter: chapter.number in chapter_number_range, base)
        if chapter_numbers:
            base = filter(lambda chapter: chapter_numbers.matches_include_exclude_pair(chapter.number), base)
        if groups:
            base = filter(
                lambda chapter: _check_values(set(chapter.groups), set(groups.include))
                and not _check_values(set(chapter.groups), set(groups.exclude)),
                base,
            )
        if users:
            base = filter(lambda chapter: users.matches_include_exclude_pair(chapter.user), base)
        final = list(base)
        if remove_duplicates:
            final = _resolve_duplicates(final, duplicate_strategy, duplicate_strategy_groups, duplicate_strategy_users)
        return type(self)(self.manga, entries=final)

    def __repr__(self) -> str:
        """Provide a string representation of the object.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}{super().__repr__()}"

    def sort(self, *, key: Optional[Callable[[Chapter], Any]] = None, reverse: bool = False):
        """Sort the ChapterList. This uses a natural sorting algorithm to sort the chapters.

        :param key: An optional key if you want to override the sorting key used by the class.
        :type key: Callable[[Chapter], Any]
        :param reverse: Whether or not to reverse the list.
        :type reverse: bool
        """
        super().sort(key=key or natsort_keygen(key=lambda chapter: chapter.name), reverse=reverse)

    async def download_all(
        self,
        *,
        skip_bad: bool = True,
        folder_format: str = "{manga}/{chapter_num}{separator}{title}",
        file_format: str = "{num}",
        as_bytes_list: bool = False,
        overwrite: bool = True,
        retries: int = 3,
        use_data_saver: bool = False,
        ssl_only: bool = False,
    ) -> Dict[Chapter, Optional[List[str]]]:
        """Download all chapters in the list.

        .. versionadded:: 0.4

        :param skip_bad: Whether or not to skip bad chapters. Defaults to True.
        :type skip_bad: bool
        :param folder_format: The format of the folder to create for the chapter. The folder can already be existing.
            The default format is ``{manga}/{chapter_num}{separator}{chapter_title}``.

            .. note::
                Specify ``.`` if you want to save the pages in the current folder.

            Available variables:

            * ``{manga}``: The name of the manga. If the chapter's manga object does not contain a title object,
              it will be fetched.
            * ``{chapter_num}``: The number of the chapter, if it exists.
            * ``{separator}``: A separator if both the chapter's number and title exists.
            * ``{title}``: The title of the chapter, if it exists.

        :type folder_format: str
        :param file_format: The format of the individual image file names. The default format is ``{num}``.

            .. note::
                The file extension is applied automatically from the real file name. There is no need to include it.

            Available variables:

            * ``{num}``: The numbering of the image files starting from 1. This respects the order the images are in
              inside of :attr:`.page_names`.
            * ``{num0}``: The same as ``{num}`` but starting from 0.
            * ``{name}``: The actual filename of the image from :attr:`.page_names`, without the file extension.

        :type file_format: str
        :param as_bytes_list: Whether or not to return the pages as a list of raw bytes. Setting this parameter to
            ``True`` will ignore the value of the ``folder_format`` parameter.
        :type as_bytes_list: bool
        :param overwrite: Whether or not to override existing files with the same name as the page. Defaults to
            ``True``.
        :type overwrite: bool
        :param retries: How many times to retry a chapter if a MD@H node does not let us download the pages.
            Defaults to ``3``.
        :type retries: int
        :param use_data_saver: Whether or not to use the data saver pages or the normal pages. Defaults to ``False``.
        :type use_data_saver: bool
        :param ssl_only: Whether or not the given URL has port ``443``. Useful if your firewall blocks outbound
            connections to ports that are not port ``443``. Defaults to ``False``.

            .. note::
                This will lower the pool of available clients and can cause higher download times.

        :type ssl_only: bool
        :raises: :class:`aiohttp.ClientResponseError` if there is an error after all retries are exhausted.
        :return: A dictionary mapping consisting of :class:`.Chapter` objects as keys and the data from that chapter's
            :meth:`.download_chapter` method. If ``skip_bad`` is True, chapters with exceptions will have ``None``
            instead of a list of bytes.
        :rtype: List[Optional[List[bytes]]]
        """
        tasks = [
            asyncio.create_task(
                item.download_chapter(
                    folder_format=folder_format,
                    file_format=file_format,
                    as_bytes_list=as_bytes_list,
                    overwrite=overwrite,
                    retries=retries,
                    use_data_saver=use_data_saver,
                    ssl_only=ssl_only,
                )
            )
            for item in self
        ]
        data = await asyncio.gather(*tasks, return_exceptions=skip_bad)
        return_mapping = {}
        for num, item in enumerate(data):
            if isinstance(item, BaseException):
                item = None
            return_mapping[self[num]] = item
        return return_mapping

    def group_by_volumes(self) -> Dict[Optional[str], List[Chapter]]:
        """Creates a dictionary mapping volume numbers to chapters.

        :return: A dictionary where the keys are volume numbers and the values are a list of :class:`.Chapter` objects.
        :rtype: Dict[Optional[str], List[Chapter]]
        """
        dd = defaultdict(list)
        for item in self:
            dd[item.volume].append(item)
        return dict(dd)

    def group_by_numbers(self) -> Dict[Optional[str], List[Chapter]]:
        """Creates a dictionary mapping chapter numbers to chapters.

        :return: A dictionary where the keys are chapter numbers and the values are a list of :class:`.Chapter` objects.
        :rtype: Dict[Optional[str], List[Chapter]]
        """
        dd = defaultdict(list)
        for item in self:
            dd[item.number].append(item)
        return dict(dd)

    def group_by_volume_and_chapters(self) -> Dict[Tuple[Optional[str], Optional[str]], List[Chapter]]:
        """Creates a dictionary mapping volume numbers and chapter numbers to chapters.

        :return: A dictionary where the keys are a tuple of volume and chapter numbers and the values are a list of
            :class:`.Chapter` objects.
        :rtype: Dict[Tuple[Optional[str], Optional[str]], List[Chapter]]
        """
        dd = defaultdict(list)
        for item in self:
            dd[(item.volume, item.number)].append(item)
        return dict(dd)

    def calculate_aggregate(self) -> MangaAggregate:
        """Calculates an aggregate of the chapters contained.

        :return: The aggregate of the chapters.
        :rtype: MangaAggregate
        """
        ma = MangaAggregate()
        for (volume_number, chapter_number), chapter in self.group_by_volume_and_chapters().items():
            ma.setdefault(volume_number, VolumeAggregate()).setdefault(chapter_number, 0)
            ma[volume_number][chapter_number] += 1
        return ma

    def locales(self) -> List[str]:
        """Get the list of locales that exist in the chapter list.

        :return: A list of locales.
        :rtype: List[str]
        """
        return list({item.language for item in self})