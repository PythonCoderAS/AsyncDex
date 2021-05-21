import asyncio
import re
import warnings
from datetime import datetime
from os import makedirs
from os.path import exists, join
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

from aiohttp import ClientError

from .abc import GenericModelList, Model
from .group import Group
from .mixins import DatetimeMixin
from .user import User
from ..constants import invalid_folder_name_regex, routes
from ..utils import copy_key_to_attribute

if TYPE_CHECKING:
    from .manga import Manga
    from ..client import MangadexClient


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

    groups: GenericModelList[Group]
    """The groups that uploaded this chapter."""

    read: bool
    """Whether or not the chapter is read."""

    def __init__(
        self,
        client: "MangadexClient",
        *,
        id: Optional[str] = None,
        version: int = 0,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.read = False
        super().__init__(client, id=id, version=version, data=data)

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
            items = await asyncio.gather(*[self.client.get_page(url) for url in pages])
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
            [item.close() for item in items]
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
        """Fetch data about the chapter. |permission| ``chapter.view``

        :raises: :class:`.InvalidID` if a chapter with the ID does not exist.
        """
        await self._fetch("chapter.view", "chapter")

    async def load_groups(self):
        """Shortcut method that calls :meth:`.MangadexClient.batch_groups` with the groups that belong to the group.

        Roughly equivalent to:

        .. code-block:: python

            await client.batch_groups(*user.groups)
        """
        await self.client.batch_groups(*self.groups)

    async def mark_read(self):
        """Mark the chapter as read. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("GET", routes["read"])
        r = await self.client.request("POST", routes["read"].format(id=self.id))
        self.read = True
        r.close()

    async def mark_unread(self):
        """Mark the chapter as unread. |auth|

        .. versionadded:: 0.5
        """
        self.client.raise_exception_if_not_authenticated("GET", routes["read"])
        r = await self.client.request("DELETE", routes["read"].format(id=self.id))
        self.read = False
        r.close()

    async def toggle_read(self):
        """Toggle a chapter between being read and unread. Requires authentication.

        .. versionadded:: 0.5

        .. note::
            This requires the read status of the chapter to be known. See :meth:`.get_read_status` or
            :meth:`.ChapterList.get_read`.

        :raises: :class:`.Unauthorized` is authentication is missing.
        """
        if self.read:
            await self.mark_unread()
        else:
            await self.mark_read()

    async def get_read(self):
        """Gets whether or not the chapter is read. The read status can then be viewed in :attr:`.read`.

        .. versionadded:: 0.5
        """
        r = await self.client.request("GET", routes["manga_read"].format(id=self.manga.id))
        self.manga._check_404(r)
        json = await r.json()
        r.close()
        self.read = self.id in json["data"]
