import asyncio
import warnings
from dataclasses import asdict
from datetime import datetime, timedelta
from json import dumps as convert_obj_to_json
from logging import NullHandler, getLogger
from types import TracebackType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Type, TypeVar, Union

import aiohttp

from .constants import ratelimit_data, routes
from .enum import ContentRating, Demographic, MangaStatus, TagMode
from .exceptions import Captcha, InvalidCaptcha, InvalidID, Ratelimit, Unauthorized
from .list_orders import AuthorListOrder, ChapterListOrder, GroupListOrder, MangaListOrder
from .models.abc import Model
from .models.author import Author
from .models.chapter import Chapter
from .models.client_user import ClientUser
from .models.custom_list import CustomList
from .models.group import Group
from .models.manga import Manga, MangaLinks
from .models.pager import Pager
from .models.tag import Tag, TagDict
from .models.title import TitleList
from .models.user import User
from .ratelimit import Ratelimits
from .utils import remove_prefix, return_date_string

logger = getLogger(__name__)
getLogger("asyncdex").addHandler(NullHandler())

_LegacyModelT = TypeVar("_LegacyModelT", Manga, Chapter, Tag, Group)


class MangadexClient:
    """The main client that runs preforms all of the method requests.

    .. warning::
        The client object should only be created under an async context. While it should be safe to initialize
        normally, the aiohttp ClientSession does not like this.

    .. warning::
        The client cannot ratelimit effectively if multiple clients are running on the same program. Furthermore,
        the ratelimit may not work if multiple other people are accessing the MangaDex API at the same time or the
        client is running on a shared network.

    :param username: The username of the user to authenticate as. Leave blank to not allow login to fetch a new
        refresh token. Specifying the username without specifying the password is an error.
    :type username: str
    :param password: The password of the user to authenticate as. Leave blank to not allow login to fetch a new
        refresh token. Specifying the password without specifying the username is an error.
    :type password: str
    :param refresh_token: The refresh token to use. Leaving the ``username`` and ``password`` parameters blank but
        specifying this parameter allows the client to make requests using the refresh token for as long as it is valid.
        Once the refresh token is invalid, if the username and password are not specified, the client will throw
        :class:`.Unauthorized`, unless :meth:`.logout` is used to set the client to anonymous
        mode.
    :type refresh_token: str
    :param sleep_on_ratelimit: Whether or not to sleep when a ratelimit occurs or raise a
        :class:`.Ratelimit`. Defaults to True.
    :type sleep_on_ratelimit: bool
    :param session: The session object for the client to use. If one is not provided, the client will create a new
        session instead. This is useful for providing a custom session.
    :type session: aiohttp.ClientSession
    :param api_url: The base URL for the MangaDex API. Useful for private instances or a testing environment. Should
        not include a trailing slash.
    :type api_url: str
    :param anonymous: Whether or not to force anonymous mode. This will clear the username and/or password.
    :type anonymous: bool
    :param session_kwargs: Optional keyword arguments to pass on to the :class:`aiohttp.ClientSession`.
    """

    api_base: str
    """The base URL for the MangaDex API, without a slash at the end."""

    username: Optional[str]
    """The username of the user that the client is logged in as. This will be None when the client is operating in 
    anonymous mode."""

    password: Optional[str]
    """The password of the user that the client is logged in as. This will be None when the client is operating in 
    anonymous mode."""

    refresh_token: Optional[str]
    """The refresh token that the client has obtained. This will be None when the client is operating in anonymous mode,
    as well as if the client has not obtained a refresh token from the API."""

    sleep_on_ratelimit: bool
    """Whether or not to sleep when a ratelimit occurs."""

    session: aiohttp.ClientSession
    """The :class:`aiohttp.ClientSession` that the client will use to make requests."""

    ratelimits: Ratelimits
    """The :class:`.Ratelimits` object that the client is using."""

    anonymous_mode: bool
    """Whether or not the client is operating in **Anonymous Mode**, where it only accesses public endpoints."""

    tag_cache: TagDict
    """A cache of tags. This cache will be used to lower the amount of tag objects, and allows for easily updating 
    the attributes of tags. This cache can be refreshed manually by either calling :meth:`.refresh_tag_cache` or 
    fetching data for any tag object.
    
    .. versionadded:: 0.2
    """

    user: ClientUser
    """The user of the client.
    
    .. versionadded:: 0.5
    """

    # Dunder methods

    def __init__(
        self,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
        sleep_on_ratelimit: bool = True,
        session: aiohttp.ClientSession = None,
        api_url: str = "https://api.mangadex.org",
        anonymous: bool = False,
        **session_kwargs,
    ):
        self.username = username
        self.password = password
        if (username, password).count(None) == 1:
            raise ValueError("Either both username and password have to be specified or neither have to be specified.")
        self.refresh_token = refresh_token
        self.sleep_on_ratelimit = sleep_on_ratelimit
        self.api_base = api_url
        self.session = session or aiohttp.ClientSession(**session_kwargs)
        self.anonymous_mode = anonymous or not (username or password or refresh_token)
        if anonymous:
            self.username = self.password = self.refresh_token = None
        self.ratelimits = Ratelimits(*ratelimit_data)
        self.tag_cache = TagDict()
        self.user = ClientUser(self)
        self._request_count = 0
        self._request_second_start = datetime.utcnow()  # Use utcnow to keep everything using UTF+0 and also helps
        # with daylight savings.
        self._request_lock = asyncio.Lock()
        self._session_token: Optional[str] = None
        self._session_token_acquired: Optional[datetime] = datetime(year=2000, month=1, day=1)
        # This is the time when the token is acquired. The client will automatically vacate the token at 15 minutes
        # and 10 seconds.

    async def __aenter__(self):
        """Allow the client to be used with ``async with`` syntax similar to :class:`aiohttp.ClientSession`."""
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ):
        """Exit the client. This will also close the underlying session object."""
        self.username = self.password = self.refresh_token = self.session_token = None
        self.anonymous_mode = True
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Provide a string representation of the client.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}(anonymous={self.anonymous_mode!r}, username={self.username!r})"

    # Request methods

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Mapping[str, Optional[Union[str, Sequence[str], bool, float]]]] = None,
        json: Any = None,
        with_auth: bool = True,
        retries: int = 3,
        allow_non_successful_codes: bool = False,
        **session_request_kwargs,
    ) -> aiohttp.ClientResponse:
        """Perform a request.

        .. warning::
            All requests have to be released, otherwise connections will not be reused. Make sure to call
            :meth:`aiohttp.ClientResponse.release` on the object returned by the method if you do not read data from
            the response.

        .. note::
            The request method will log all URLs that are requested. Enable logging on the ``asyncdex`` logger to
            view them. These requests are made under the ``INFO`` level. Retries are also logged on the ``WARNING``
            level.

        .. versionchanged:: 0.3
            Added a global (shared between all requests made in the client) ratelimit.

        .. versionchanged:: 0.4
            Added better handling of string items.

        :param method: The HTTP method to use for the request.
        :type method: str
        :param url: The URL to use for the request. May be either an absolute URL or a URL relative to the base
            MangaDex API URL.
        :type url: str
        :param params: Optional query parameters to append to the URL. If one of the values of the parameters is an
            array, the elements will be automatically added to the URL in the order that the array elements appear in.
        :type params: Mapping[str, Union[str, Sequence[str]]]
        :param json: JSON data to pass in a POST request.
        :type json: Any
        :param with_auth: Whether or not to append the session token to the request headers. Requests made without
            the header will behave as if the client is in anonymous mode. Defaults to ``True``.
        :type with_auth: bool
        :param retries: The amount of times to retry. The function will recursively call itself, subtracting ``1``
            from the original count until retries run out.
        :type retries: int
        :param allow_non_successful_codes: Whether or not to allow non-success codes (4xx codes that aren't 401/429)
            to pass through instead of raising an error. False by default
        :type allow_non_successful_codes: bool
        :param session_request_kwargs: Optional keyword arguments to pass to :meth:`aiohttp.ClientSession.request`.
        :raises: :class:`.Unauthorized` if the endpoint requires authentication and sufficient parameters for
            authentication were not provided to the client.
        :raises: :class`aiohttp.ClientResponseError` if the response is a 4xx or 5xx code after multiple retries or
            if it will not be retried and ``allow_non_successful_codes`` is False.
        :return: The response.
        :rtype: aiohttp.ClientResponse
        """
        if url.startswith("/"):  # Add the base URL if the base URL is not an absolute URL.
            url = self.api_base + url
        if params:
            # Strategy: Put all the parts into a list, and then use "&".join(<arr>) to add all the parts together
            param_parts = []
            for name, value in params.items():
                if not isinstance(value, str) and hasattr(value, "__iter__"):
                    for item in value:
                        param_parts.append(f"{name}[]={item}")
                elif isinstance(value, str):
                    param_parts.append(f"{name}={value}")
                else:
                    param_parts.append(f"{name}={convert_obj_to_json(value)}")
            url += "?" + "&".join(param_parts)
        headers = {}
        if with_auth and not self.anonymous_mode:
            if self.session_token is None:
                await self.get_session_token()
            headers["Authorization"] = f"Bearer {self.session_token}"
        path_obj = None
        if url.startswith(self.api_base):
            # We only want the ratelimit to only apply to the API urls.
            async with self._request_lock:
                # I decided not to throw exceptions for these 1-second ratelimits.
                self._request_count += 1
                time_now = datetime.utcnow()
                time_difference = (time_now - self._request_second_start).total_seconds()
                if time_difference <= 1.25 and self._request_count >= 5:  # Hopefully this will stop excess retries
                    # which cripple pagers.
                    logger.warning("Sleeping for 1.25 seconds.")
                    await asyncio.sleep(1.25)
                elif time_difference > 1:
                    self._request_count = 0
                    self._request_second_start = time_now
            if self.sleep_on_ratelimit:
                path_obj = await self.ratelimits.sleep(remove_prefix(self.api_base, url), method)
            else:
                time_to_sleep, path_obj = await self.ratelimits.check(remove_prefix(self.api_base, url), method)
                if time_to_sleep > 0 and path_obj:
                    raise Ratelimit(path_obj.path.name, path_obj.ratelimit_amount, path_obj.ratelimit_expires)
        logger.info("Making %s request to %s", method, url)
        resp = await self.session.request(method, url, headers=headers, json=json, **session_request_kwargs)
        if path_obj:
            path_obj.update(resp)
        do_retry = False
        if url.startswith(self.api_base):
            if resp.status == 401:  # Unauthorized
                if self.session_token:  # Invalid session token
                    await self.get_session_token()
                    do_retry = True
                elif self.username and self.password:  # Invalid refresh token
                    await self.login()
                    do_retry = True
                else:
                    try:
                        raise Unauthorized(method, url, resp)
                    finally:
                        await resp.release()
            elif resp.status in [403, 412]:
                site_key = resp.headers.get("X-Captcha-Sitekey", "")
                if site_key:
                    raise Captcha(site_key, method, url, resp)
            elif resp.status == 429:  # Ratelimit error. This should be handled by ratelimits but I'll handle it here as
                # well.
                if resp.headers.get("x-ratelimit-retry-after", ""):
                    diff = (
                        datetime.utcfromtimestamp(int(resp.headers["x-ratelimit-retry-after"])) - datetime.utcnow()
                    ).total_seconds()
                    logger.warning("Sleeping for %s seconds.", diff)
                    await asyncio.sleep(diff)
                else:
                    logger.warning("Sleeping for 1.25 seconds.")
                    await asyncio.sleep(
                        1.25
                    )  # This is probably the result of multiple devices, so sleep for a second. Will
                    # give up on the 4th try though if it is persistent.
                do_retry = True
        if resp.status // 100 == 5:  # 5xx
            do_retry = True
        if do_retry:
            if retries > 0:
                logger.warning("Retrying %s request to %s because of HTTP code %s", method, url, resp.status)
                return await self.request(
                    method, url, json=json, with_auth=with_auth, retries=retries - 1, **session_request_kwargs
                )
            else:
                resp.raise_for_status()
        elif not allow_non_successful_codes:
            resp.raise_for_status()
        return resp

    async def _one_off(self, method, url, *, params=None, json=None, with_auth=True, retries=3, **kwargs):
        """Use for one-off requests where we do not care about the response."""
        r = await self.request(method, url, params=params, json=json, with_auth=with_auth, retries=retries, **kwargs)
        r.close()

    async def _get_json(self, method, url, *, params=None, json=None, with_auth=True, retries=3, **kwargs):
        """Used for getting the json quickly when we don't care about request codes."""
        r = await self.request(method, url, params=params, json=json, with_auth=with_auth, retries=retries, **kwargs)
        json = await r.json()
        r.close()
        return json

    # Authentication

    def raise_exception_if_not_authenticated(self, method: str, path: str):
        """Raise an exception if authentication is missing. This is ideally used before making requests that will
        always need authentication.

        .. versionadded:: 0.5

        :param method: The method to show.

            .. seealso:: :attr:`.Unauthorized.method`.

        :type method: str
        :param path: The path to display.

            .. seealso:: :attr:`.Unauthorized.path`.

        :type path: str
        :raises: :class:`.Unauthorized`
        """
        if self.anonymous_mode:
            raise Unauthorized(method, path, None)

    @property
    def session_token(self) -> Optional[str]:
        """The session token tht the client has obtained. This will be None when the client is operating in anonymous
        mode, as well as if the client has not obtained a refresh token from the API or if it has been roughly 15
        minutes since the token was retrieved from the server."""
        if datetime.utcnow() - self._session_token_acquired > timedelta(minutes=15, seconds=10):
            self._session_token = None
        return self._session_token

    @session_token.setter
    def session_token(self, token: Optional[str]):
        """Set the session token and the access time

        :param token: The new session token
        :type token: str
        :return: None
        :rtype: None
        """
        self._session_token = token
        if token:
            self._session_token_acquired = datetime.utcnow()
        else:
            self._session_token_acquired = datetime(year=2000, month=1, day=1)

    async def get_session_token(self):
        """Get the session token and store it inside the client."""
        if self.refresh_token is None:
            await self.login()
        r = await self.request("POST", routes["session_token"], json={"token": self.refresh_token}, with_auth=False)
        data = await r.json()
        r.close()
        self.session_token = data["token"]["session"]
        self.refresh_token = data["token"]["refresh"]
        if self.user.id == "client-user":
            await self.user.fetch()

    async def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """Logs in to the MangaDex API.

        :param username: Provide a username in order to make the client stop running in anonymous mode. Specifying
            the username without specifying the password is an error.
        :type username: str
        :param password: Provide a password in order to make the client stop running in anonymous mode. Specifying
            the password without specifying the username is an error.
        :type password: str
        """
        if (username, password).count(None) == 1:
            raise ValueError("Either both username and password have to be specified or neither have to be specified.")
        if username and password:
            self.username = username
            self.password = password
            self.anonymous_mode = False
        elif not (self.username and self.password):
            self.raise_exception_if_not_authenticated("POST", routes["login"])
        r = await self.request(
            "POST", routes["login"], json={"username": self.username, "password": self.password}, with_auth=False
        )
        data = await r.json()
        r.close()
        self.session_token = data["token"]["session"]
        self.refresh_token = data["token"]["refresh"]
        await self.user.fetch()

    async def logout(self, delete_tokens: bool = True, clear_login_info: bool = True):
        """Log out from the API.

        :param delete_tokens: Whether or not to delete the refresh/session tokens by calling the logout endpoint.
            Defaults to true.

            .. versionadded:: 0.5

        :type delete_tokens: bool
        :param clear_login_info: Whether or not to clear login info from the client, so that future logins are not
            possible without a new token or calling :meth:`.login` with the ``username`` and ``password`` parameters.
            Defaults to true.

            .. versionadded:: 0.5

        :type clear_login_info: bool
        """
        if (self.refresh_token or self.session_token) and delete_tokens:
            (await self.request("POST", routes["logout"])).release()
            self.refresh_token = self.session_token = None
        if clear_login_info:
            self.username = self.password = self.refresh_token = self.session_token = None
            self.anonymous_mode = True
            self.user = ClientUser(self)

    # Methods to get models

    async def refresh_tag_cache(self):
        """Refresh the internal tag cache.

        .. versionadded:: 0.2
        .. seealso:: :attr:`.tag_cache`
        """
        r = await self.request("GET", routes["tag_list"])
        json = await r.json()
        r.close()
        for item in json:
            assert item["data"]["id"], "ID missing from tag list"
            tag_id = item["data"]["id"]
            new_tag = Tag(self, data=item)
            if tag_id in self.tag_cache:
                old_tag = self.tag_cache[tag_id]
                old_tag.transfer(new_tag)
            else:
                self.tag_cache[new_tag.id] = new_tag

    async def get_tag(self, id: str) -> Tag:
        """Get a tag using it's ID.

        .. versionadded:: 0.2

        .. admonition:: Finding a Tag by Name

            Finding a tag by name is a feature that many people want. However, there is no endpoint that exists in
            the API that lets us provide a name and get back a list of Tags that match the name. It is not needed,
            as there only exists a relatively amount of tags, which can be loaded from a single request.

            The client maintains a cache of the tags in order to lower memory usage and allow tag updates to be
            easily distributed to all mangas, since there are a relatively small amount of tags compared to authors,
            chapters, mangas, and users. The client also provides a method to completely load the tag list and update
            the tag cache, :meth:`.refresh_tag_cache`. The tag cache is stored in :attr:`.tag_cache`, Using this
            property, it is possible to iterate over the tag list and preform a simple name matching search to find
            the tag(s) that you want. An example implementation of a tag search method is provided as such:

            .. code-block:: python

                from asyncdex import MangadexClient, Tag
                from typing import List

                def search_tags(client: MangadexClient, phrase: str) -> List[Tag]:
                    phrase = phrase.replace(" ", "") # Remove spaces so "sliceoflife" and "slice of life" match.
                    results: List[Tag] = []
                    for tag in client.tag_cache:
                        for name in tag.names.values():
                            if phrase in name.replace(" ", "").lower():
                                results.append(tag)
                                break
                    return results

        :param id: The tag's UUID.
        :type id: str
        :return: A :class:`.Tag` object.
        :rtype: Tag
        """
        if id in self.tag_cache:
            return self.tag_cache[id]
        else:
            await self.refresh_tag_cache()
            if id in self.tag_cache:
                return self.tag_cache[id]
            else:
                raise InvalidID(id, Tag)

    def get_manga(self, id: str) -> Manga:
        """Get a manga using it's ID.

        .. versionadded:: 0.2

        .. seealso:: :meth:`.search`.

        .. warning::
            This method returns a **lazy** Manga instance. Call :meth:`.Manga.fetch` on the returned object to see
            any values.

        :param id: The manga's UUID.
        :type id: str
        :return: A :class:`.Manga` object.
        :rtype: Manga
        """
        return Manga(self, id=id)

    async def random_manga(self) -> Manga:
        """Get a random manga.

        .. versionadded:: 0.2

        :return: A random manga.
        :rtype: Manga
        """
        r = await self.request("GET", routes["random_manga"])
        try:
            return Manga(self, data=await r.json())
        finally:
            r.close()

    def get_author(self, id: str) -> Author:
        """Get an author using it's ID.

        .. versionadded:: 0.2

        .. note::
            This method can also be used to get artists, since they are the same class.

        .. warning::
            This method returns a **lazy** Author instance. Call :meth:`.Author.fetch` on the returned object to see
            any values.

        :param id: The author's UUID.
        :type id: str
        :return: A :class:`.Author` object.
        :rtype: Author
        """
        return Author(self, id=id)

    def get_chapter(self, id: str) -> Chapter:
        """Get a chapter using it's ID.

        .. versionadded:: 0.3

        .. seealso:: :meth:`.ChapterList.get`.

        .. warning::
            This method returns a **lazy** Chapter instance. Call :meth:`.Chapter.fetch` on the returned object to see
            any values.

        :param id: The chapter's UUID.
        :type id: str
        :return: A :class:`.Chapter` object.
        :rtype: Chapter
        """
        return Chapter(self, id=id)

    def get_user(self, id: str) -> User:
        """Get a user using it's ID.

        .. versionadded:: 0.3

        .. warning::
            This method returns a **lazy** User instance. Call :meth:`.User.fetch` on the returned object to see
            any values.

        :param id: The user's UUID.
        :type id: str
        :return: A :class:`.User` object.
        :rtype: User
        """
        return User(self, id=id)

    async def logged_in_user(self) -> User:
        """Get the user that is currently logged in.

        .. versionadded:: 0.3

        .. deprecated:: 0.5
            Use :attr:`.user` and :meth:`.ClientUser.fetch_user`

        :return: A :class:`.User` object.
        :rtype: User
        """
        warnings.warn(
            "MangadexClient.logged_in_user is deprecated. Use MangadexClient.user and " "ClientUser.fetch_user().",
            category=DeprecationWarning,
            stacklevel=2,
        )
        await self.user.fetch_user()
        return self.user

    def get_group(self, id: str) -> Group:
        """Get a group using it's ID.

        .. versionadded:: 0.3

        .. warning::
            This method returns a **lazy** Group instance. Call :meth:`.Group.fetch` on the returned object to see
            any values.

        :param id: The group's UUID.
        :type id: str
        :return: A :class:`.Group` object.
        :rtype: Group
        """
        return Group(self, id=id)

    def get_list(self, id: str) -> CustomList:
        """Get a custom list using it's ID.

        .. versionadded:: 0.5

        .. warning::
            This method returns a **lazy** CustomList instance. Call :meth:`.CustomList.fetch` on the returned object
            to see
            any values.

        :param id: The custom list's UUID.
        :type id: str
        :return: A :class:`.CustomList` object.
        :rtype: CustomList
        """
        return CustomList(self, id=id)

    # Batch models

    async def _do_batch(self, items: Tuple[Model, ...], permission: str, route_name: str):
        self.user.permission_exception(permission, "GET", routes[route_name])
        uuid_map: Dict[str, List[Model]] = {}
        for item in items:
            uuid_map.setdefault(item.id, []).append(item)
        req_list = []
        uuids = list(uuid_map.keys())
        while uuids:
            uuids_for_this_batch = uuids[:100]
            assert len(uuids_for_this_batch) <= 100, "Why?"
            uuids = uuids[100:]
            req_list.append(
                asyncio.create_task(
                    self._get_json("GET", routes[route_name], params=dict(limit=100, ids=uuids_for_this_batch))
                )
            )
        data = await asyncio.gather(*req_list)
        for results in data:
            for item in results["results"]:
                item_id = item["data"]["id"]
                assert item_id, "Missing ID"
                for obj in uuid_map[item_id]:
                    obj.parse(item)

    async def batch_authors(self, *authors: Author):
        """Updates a lot of authors at once, reducing the time needed to update tens or hundreds of authors.
        |permission| ``author.list``

        .. versionadded:: 0.2

        :param authors: A tuple of all the authors (and artists) to update.
        :type authors: Tuple[Author, ...]
        """
        await self._do_batch(authors, "author.list", "author_list")

    async def batch_mangas(self, *mangas: Manga):
        """Updates a lot of mangas at once, reducing the time needed to update tens or hundreds of mangas.
        |permission| ``manga.list``

        .. versionadded:: 0.2

        :param mangas: A tuple of all the mangas to update.
        :type mangas: Tuple[Manga, ...]
        """
        await self._do_batch(mangas, "manga.list", "search")

    async def batch_chapters(self, *chapters: Chapter):
        """Updates a lot of chapters at once, reducing the time needed to update tens or hundreds of chapters.
        |permission| ``chapter.list``

        .. versionadded:: 0.3

        .. seealso:: :meth:`.ChapterList.get`.

        :param chapters: A tuple of all the chapters to update.
        :type chapters: Tuple[Chapter, ...]
        """
        await self._do_batch(chapters, "chapter.list", "chapter_list")

    async def batch_groups(self, *groups: Group):
        """Updates a lot of groups at once, reducing the time needed to update tens or hundreds of groups.
        |permission| ``scanlation_group.list``

        .. versionadded:: 0.3

        :param groups: A tuple of all the groups to update.
        :type groups: Tuple[Group, ...]
        """
        await self._do_batch(groups, "scanlation_group.list", "group_list")

    async def batch_manga_read(self, *mangas: Manga):
        """Find the read status for multiple mangas. |auth|

        .. versionadded:: 0.5

        :param mangas: A tuple of manga objects.
        :type mangas: Tuple[Manga, ...]
        """
        # We can't use _do_batch here unfortunately.
        self.raise_exception_if_not_authenticated("GET", routes["batch_manga_read"])
        final_data = []
        manga_list = list({manga.id for manga in mangas})
        while manga_list:
            batch = manga_list[:100]
            manga_list = manga_list[100:]
            r = await self.request("GET", routes["batch_manga_read"], params={"ids": batch})
            json = await r.json()
            r.close()
            final_data.extend(json["data"])
        for item in mangas:
            item.chapters._update_read_data({"data": final_data})

    # Get lists

    @staticmethod
    def _add_order(
        params: Dict[str, Any],
        order: Optional[Union[GroupListOrder, AuthorListOrder, ChapterListOrder, MangaListOrder]],
    ):
        if order:
            params["order"] = {k: v.value for k, v in asdict(order) if v}

    def get_groups(
        self, *, name: Optional[str] = None, order: Optional[GroupListOrder] = None, limit: Optional[int] = None
    ) -> Pager[Group]:
        """Creates a :class:`.Pager` for groups. |permission| ``scanlation_group.list``

        .. versionadded:: 0.4

        Usage:

        .. code-block:: python

            async for group in client.get_groups(name="Group Name"):
                ...

        :param name: The name to search for.
        :type name: str
        :param order: The order to sort the groups [#V506_CHANGELOG]_.
        :type order: GroupListOrder
        :param limit: Only return up to this many groups.

            .. note::
                Not setting a limit when you are only interested in a certain amount of responses may result in the
                Pager making more requests than necessary, consuming ratelimits.

        :type limit: int
        :return: A Pager for the groups.
        :rtype: Pager
        """
        params = {}
        if name:
            params["name"] = name.replace(" ", "+")
        self._add_order(params, order)
        self.user.permission_exception("scanlation_group.list", "GET", routes["group_list"])
        return Pager(routes["group_list"], Group, self, params=params, limit=limit)

    def get_chapters(
        self,
        *,
        title: Optional[str] = None,
        groups: Optional[Sequence[Union[str, Group]]] = None,
        uploader: Optional[Union[str, User]] = None,
        manga: Optional[Union[str, Manga]] = None,
        volume: Optional[str] = None,
        chapter_number: Optional[str] = None,
        language: Optional[str] = None,
        created_after: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        published_after: Optional[datetime] = None,
        order: Optional[ChapterListOrder] = None,
        limit: Optional[int] = None,
    ) -> Pager[Chapter]:
        """Gets a :class:`.Pager` of chapters. |permission| ``chapter.list``

        .. versionadded:: 0.4

        Usage:

        .. code-block:: python

            async for chapter in client.get_chapters(chapter_number="1"):
                ...

        :param title: The title of the chapter.
        :type title: str
        :param groups: Chapters made by one of the groups in the given list. A group can either be the UUID of the
            group in string format or an instance of :class:`.Group`.
        :type groups: List[Union[str, Group]]
        :param uploader: The user who uploaded the chapter. A user can either be the UUID of the user in string
            format or an instance of :class:`.User`.
        :type uploader: Union[str, User]
        :param manga: Chapters that belong to the given manga. A manga can either be the UUID of the manga in string
            format or an instance of :class:`.Manga`.

            .. note::
                If fetching all chapters for one manga, it is more efficient to use :meth:`.ChapterList.get` instead.

        :type manga: Union[str, Manga]
        :param volume: The volume that the chapter belongs to.
        :type volume: str
        :param chapter_number: The number of the chapter.
        :type chapter_number: str
        :param language: The language of the chapter.
        :type language: str
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
        :param order: The order to sort the chapters.
        :type order: ChapterListOrder
        :param limit: Only return up to this many chapters.

            .. note::
                Not setting a limit when you are only interested in a certain amount of responses may result in the
                Pager making more requests than necessary, consuming ratelimits.

        :type limit: int
        :return: A Pager for the chapters.
        :rtype: Pager
        """
        params = {}
        if title:
            params["title"] = title.replace(" ", "+")
        if groups:
            params["groups"] = [str(item) for item in groups]
        if uploader:
            params["uploader"] = str(uploader)
        if manga:
            params["manga"] = str(manga)
        if volume:
            params["volume"] = volume
        if chapter_number:
            params["chapter"] = chapter_number
        if language:
            params["translatedLanguage"] = language
        if created_after:
            params["createdAtSince"] = return_date_string(created_after)
        if updated_after:
            params["updatedAtSince"] = return_date_string(updated_after)
        if published_after:
            params["publishAtSince"] = return_date_string(published_after)
        self._add_order(params, order)
        self.user.permission_exception("chapter.list", "GET", routes["chapter_list"])
        return Pager(routes["chapter_list"], Chapter, self, params=params, limit=limit)

    def get_authors(
        self, *, name: Optional[str] = None, order: Optional[AuthorListOrder] = None, limit: Optional[int] = None
    ) -> Pager[Author]:
        """Creates a :class:`.Pager` for authors. |permission| ``author.list``

        .. versionadded:: 0.4

        Usage:

        .. code-block:: python

            async for author in client.get_authors(name="Author Name"):
                ...

        :param name: The name to search for.
        :type name: str
        :param order: The order to sort the authors [#V506_CHANGELOG]_.
        :type order: AuthorListOrder
        :param limit: Only return up to this many authors.

            .. note::
                Not setting a limit when you are only interested in a certain amount of responses may result in the
                Pager making more requests than necessary, consuming ratelimits.

        :type limit: int
        :return: A Pager for the authors.
        :rtype: Pager
        """
        params = {}
        if name:
            params["name"] = name.replace(" ", "+")
        self._add_order(params, order)
        self.user.permission_exception("author.list", "GET", routes["author_list"])
        return Pager(routes["author_list"], Author, self, params=params, limit=limit)

    def get_mangas(
        self,
        *,
        title: Optional[str] = None,
        authors: Optional[List[Union[str, Author]]] = None,
        artists: Optional[List[Union[str, Author]]] = None,
        year: Optional[int] = None,
        included_tags: Optional[List[Union[str, Tag]]] = None,
        included_tag_mode: TagMode = TagMode.AND,
        excluded_tags: Optional[List[Union[str, Tag]]] = None,
        excluded_tag_mode: TagMode = TagMode.OR,
        status: Optional[List[MangaStatus]] = None,
        languages: Optional[List[str]] = None,
        demographic: Optional[List[Demographic]] = None,
        rating: Optional[List[ContentRating]] = None,
        created_after: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        order: Optional[MangaListOrder] = None,
        limit: Optional[int] = None,
    ) -> Pager[Manga]:
        """Gets a :class:`.Pager` of mangas. |permission| ``manga.list``

        .. versionadded:: 0.4

        Usage:

        .. code-block:: python

            async for manga in client.search(title="Solo Leveling"):
                ...

        :param title: The title of the manga.
        :type title: str
        :param authors: Mangas made by the given authors. An author may be represented by a string containing their UUID
            or an instance of :class:`.Author`.
        :type authors: List[Union[str, Author]]
        :param artists: Mangas made by the given artists. An artist may be represented by a string containing their UUID
            or an instance of :class:`.Author`.
        :type artists: List[Union[str, Author]]
        :param year: The year the manga was published.
        :type year: int
        :param included_tags: A list of tags that should be present. A tag may be represented by a string containing
            the tag's UUID or an instance of :class:`.Tag`.
        :type included_tags: List[Union[str, Tag]]
        :param included_tag_mode: The mode to use for the included tags. Defaults to :attr:`.TagMode.AND`.
        :type included_tag_mode: TagMode
        :param excluded_tags: A list of tags that should not be present. A tag may be represented by a string containing
            the tag's UUID or an instance of :class:`.Tag`.
        :type excluded_tags: List[Union[str, Tag]]
        :param excluded_tag_mode: The mode to use for the excluded tags. Defaults to :attr:`.TagMode.OR`.
        :type excluded_tag_mode: TagMode
        :param status: A list of :class:`.MangaStatus`\ es representing possible statuses.
        :type status: List[MangaStatus]
        :param languages: A list of language coes.
        :type languages: List[str]
        :param demographic: A list of :class:`.Demographic`\ s representing possible demographics.
        :type demographic: List[Demographic]
        :param rating: A list of :class:`.ContentRating`\ s representing possible content ratings.
        :param created_after: Get mangas created after this date.

            .. note::
                The datetime object needs to be in UTC time. It does not matter if the datetime if naive or timezone
                aware.

        :type created_after: datetime
        :param updated_after: Get mangas updated after this date.

            .. note::
                The datetime object needs to be in UTC time. It does not matter if the datetime if naive or timezone
                aware.

        :type updated_after: datetime
        :param limit: Only return up to this many mangas.

            .. note::
                Not setting a limit when you are only interested in a certain amount of responses may result in the
                Pager making more requests than necessary, consuming ratelimits.

        :param order: The order to sort the mangas.
        :type order: MangaListOrder
        :type limit: int
        :return: A Pager with the manga entries.
        :rtype: Pager
        """
        params = {"includedTagsMode": included_tag_mode.value, "excludedTagsMode": excluded_tag_mode.value}
        if title:
            params["title"] = title.replace(" ", "+")
        if authors:
            params["authors"] = [str(item) for item in authors]
        if artists:
            params["artists"] = [str(item) for item in artists]
        if year:
            params["year"] = year
        if included_tags:
            params["includedTags"] = [str(item) for item in included_tags]
        if excluded_tags:
            params["excludedTags"] = [str(item) for item in excluded_tags]
        if status:
            params["status"] = [item.value for item in status]
        if languages:
            params["originalLanguage"] = languages
        if demographic:
            params["publicationDemographic"] = [item.value for item in demographic]
        if rating:
            params["contentRating"] = [item.value for item in rating]
        if created_after:
            params["createdAtSince"] = return_date_string(created_after)
        if updated_after:
            params["updatedAtSince"] = return_date_string(updated_after)
        self._add_order(params, order)
        self.user.permission_exception("manga.list", "GET", routes["search"])
        return Pager(routes["search"], Manga, self, params=params, limit=limit)

    search = get_mangas
    """Alias for :meth:`.get_mangas`."""

    # Create methods

    async def create_author(self, name: str) -> Author:
        """Create a new author. |auth| |permission| ``author.create``

        .. versionadded:: 0.5

        :param name: The author's name.
        :type name: str
        :return: The new author.
        :rtype: Author
        """
        params = {"name": name}
        self.raise_exception_if_not_authenticated("POST", routes["author_list"])
        self.user.permission_exception("author.create", "POST", routes["author_list"])
        r = await self.request("POST", routes["author_list"], json=params)
        json = await r.json()
        r.close()
        return Author(self, data=json)

    async def create_group(self, name: str, members: Optional[List[User]], *, leader: Optional[User] = None) -> Group:
        """Create a scanlation group. |auth| |permission| ``scanlation_group.create``

        .. versionadded:: 0.5

        :param name: The name of the group.
        :type name: str
        :param members: The members of the group.
        :type members: List[User]
        :param leader: The leader of the group. Defaults to the logged in user.
        :type leader: User
        :return: A new group.
        :rtype: Group
        """
        leader = leader or self.user
        params = {"name": name, "members": [item.id for item in members], "leader": leader.id}
        self.raise_exception_if_not_authenticated("POST", routes["group_list"])
        self.user.permission_exception("scanlation_group.create", "POST", routes["group_list"])
        r = await self.request("POST", routes["group_list"], json=params)
        json = await r.json()
        r.close()
        return Group(self, data=json)

    async def create_manga(
        self,
        *,
        title: Optional[Dict[str, str]] = None,
        alt_titles: Optional[List[Dict[str, str]]] = None,
        descriptions: Optional[Dict[str, str]] = None,
        authors: Optional[List[Union[str, Author]]] = None,
        artists: Optional[List[Union[str, Author]]] = None,
        links: Optional[MangaLinks] = None,
        language: Optional[str] = None,
        last_volume: Optional[str] = None,
        last_chapter_number: Optional[str] = None,
        demographic: Optional[Demographic] = None,
        status: Optional[MangaStatus] = None,
        year: Optional[int] = None,
        rating: Optional[ContentRating] = None,
        notes: Optional[str] = None,
        all_titles: Optional[Dict[str, TitleList]] = None,
    ) -> Manga:
        """Create a manga. |auth| |permission| ``manga.create``

        .. versionadded:: 0.5

        .. note::
            New mangas have to be approved by the mod team.

        :param title: The titles of the manga.

            .. note::
                See the documentation for the ``all_titles`` parameter to learn how to add all titles in one dictionary.

        :type title: Dict[str, str]
        :param alt_titles: Alternate titles to use.
        :type alt_titles: List[Dict[str, str]]
        :param all_titles: A dictionary of a language code key and a :class:`.TitleList` as values.

            .. warning:: Using ``title`` and ``all_titles`` will overwrite any values in the dictionary provided to
                ``title`` if a corresponding title for the same language code is found in ``all_titles``.

            .. admonition:: Using ``all_titles`` to set titles:

                .. code-block:: python

                    from asyncdex import AttrDict, TitleList

                    titles_en = ["Primary", "secondary", "tertiary"]
                    titles_es = ["Primero, "segundo"]
                    title_dict = AttrDict()
                    title_dict["en"] = TitleList(titles_en)
                    title_dict["es"] = TitleList(titles_es)

                    manga = await client.create_manga(..., all_titles=title_dict)

        :type all_titles: Dict[str, TitleList]
        :param descriptions: A dictionary of language codes to descriptions for that language.
        :type descriptions: Dict[str, str]
        :param authors: A list of either :class:`.Author` objects or author UUIDs.
        :type authors: List[Author]
        :param artists: A list of either :class:`.Author` objects or author UUIDs.
        :type artists: List[Author]
        :param links: An instance of :class:`.MangaLinks` containing the IDs for the manga.
        :type links: MangaLinks
        :param language: The original language of the manga.
        :type language: str
        :param last_volume: The number of the last volume.
        :type last_volume: str
        :param last_chapter_number: The number of the last chapter.
        :type last_chapter_number: str
        :param demographic: The manga's demographic, or ``None`` to have no demographic.
        :type demographic: Optional[Demographic]
        :param status: The manga's status, or ``None`` to have no status.
        :type status: Optional[MangaStatus]
        :param year: The year the manga started publication.
        :type year: int
        :param rating: The manga's content rating, or ``None`` to use the default.
        :type rating: Optional[CotentRating]
        :param notes: Optional notes to show to a moderator.
        :type notes: str
        :raise: :class:`ValueError` if the ``title`` field is None.
        :return: The new manga.
        :rtype: Manga
        """
        title = title or {}
        alt_titles = alt_titles or []
        all_titles = all_titles or {}
        for lang, titles in all_titles.items():
            primary, alternates = titles.parts()
            title[lang] = primary
            for item in alternates:
                alt_titles.append({lang: item})
        if not title:
            raise ValueError("A title needs to be specified.")
        params = {
            "title": title,
            "lastVolume": last_volume,
            "lastChapter": last_chapter_number,
            "publicationDemographic": demographic.value if demographic else None,
            "status": status.value if status else None,
            "contentRating": rating.value if rating else None,
            "modNotes": notes,
        }
        if alt_titles:
            params["altTitles"] = alt_titles
        if descriptions:
            params["description"] = descriptions
        if authors:
            params["authors"] = [str(item) for item in authors]
        if artists:
            params["artists"] = [str(item) for item in artists]
        if links:
            params["links"] = links.to_dict()
        if language:
            params["originalLanguage"] = language
        if year:
            params["year"] = year
        self.raise_exception_if_not_authenticated("POST", routes["search"])
        self.user.permission_exception("manga.create", "POST", routes["search"])
        r = await self.request("POST", routes["search"], json=params)
        json = await r.json()
        r.close()
        return Manga(self, data=json)

    # Account methods

    async def create(
        self, username: str, password: str, email: str, login: bool = True, store_credentials: bool = True
    ):
        """Create an account.

        .. versionadded:: 0.5

        :param username: The username of the account.
        :type username: str
        :param password: The password of the account.
        :type password: str
        :param email: The email of the account.
        :type email: str
        :param login: Whether or not to log in to the API using the new account credentials. Defaults to ``True``.
        :type login: bool
        :param store_credentials: Whether or not to store the credentials inside the client class. Defaults to ``True``.

            .. note::
                If the credentials are not stored but ``login`` is True, then the client will operate in refresh
                token only mode.
        :type store_credentials: bool
        """
        await self.request(
            "POST",
            routes["create_account"],
            json={"username": username, "password": password, "email": email},
            with_auth=False,
        )
        if login:
            await self.login(username, password)
            if not store_credentials:
                self.username = self.password = None
        elif store_credentials:
            self.username = username
            self.password = password

    async def activate_account(self, code: str):
        """Activate a MangaDex account.

        .. versionadded:: 0.5

        :param code: The code to activate.
        :type code: str
        """
        await self.request("GET", routes["activate_account"].format(code=code), with_auth=False)

    async def resend_activation_code(self, email: str):
        """Resend an activation email.

        .. versionadded:: 0.5

        :param email: The email to resend to
        :type email: str
        """
        await self.request("POST", routes["resend"], json={"email": email}, with_auth=False)

    async def reset_password_email(self, email: str):
        """Start the process of resetting an account's password.

        .. versionadded:: 0.5

        :param email: The email of the account to reset the password of.
        :type email: str
        """
        await self.request("POST", routes["start_recover"], json={"email": email}, with_auth=False)

    async def finish_password_reset(self, code: str, new_password: str, store_new_password: bool = True):
        """Finish the password reset process.

        .. versionadded:: 0.5

        .. warning::
            The MangaDex API fails silently on password resets, meaning that if a password reset fails it will not
            tell you. Instead, future login attempts will fail. You can check if a reset is valid by calling
            :meth:`.login` with the username and new password. If it returns 401 then the password reset failed.

        :param code: The code obtained from the sent email.
        :type code: str
        :param new_password: The new password to set. Needs to be >8 characters.
        :type new_password: str
        :param store_new_password: Whether or not to store the password in the client. The password will not be
            stored if a corresponding username is not stored in the client class. Defaults to ``True``.
        :type store_new_password: bool
        :raises: :class:`ValueError` if the password is <8 characters.
        """
        if len(new_password) < 8:
            raise ValueError("Password must be >=8 characters.")
        await self.request(
            "POST", routes["finish_recover"].format(code=code), json={"newPassword": new_password}, with_auth=False
        )
        if store_new_password and self.username:
            self.password = new_password

    # Misc methods

    async def ping(self):
        """Ping the server. This will throw an error if there is any error in making connections, whether with the
        client or the server.

        .. versionadded:: 0.3
        """
        return await self._one_off("GET", routes["ping"])

    async def solve_captcha(self, answer: str):
        """Solve the captcha.

        .. versionadded:: 0.5

        :param answer: The answer to the captcha.
        :type answer: str
        :raises: :class:`.InvalidCaptcha` if the captcha is invalid.
        """
        r = await self.request(
            "POST", routes["captcha"], json={"captchaChallenge": answer}, allow_non_successful_codes=True
        )
        if not r.ok:
            raise InvalidCaptcha(r)
        else:
            r.close()

    async def convert_legacy(self, model: Type[_LegacyModelT], ids: List[int]) -> Dict[int, _LegacyModelT]:
        """Convert a list of legacy IDs to the new UUID system.

        .. versionadded:: 0.3

        :param model: The model that represents the type of conversion. The endpoint allows conversions of old
            mangas, chapters, tags, and groups.
        :type model: Type[Manga, Chapter, Tag, Group]
        :param ids: The list of integer IDs to convert.
        :type ids: List[int]
        :return: A dictionary mapping old IDs to instances of the model with the new UUIDs.

            .. note::
                Except for tags, all other models will be lazy models. However, batch methods exist for all other
                models.

        :rtype: Dict[int, Model]
        """
        conversion_map = {}
        enqueued = []
        for i in range(1000, len(ids), 1000):
            enqueued.append(asyncio.create_task(self.convert_legacy(model, ids[i : i + 1000])))
        ids = ids[:1000]
        if enqueued:
            data = await asyncio.gather(*enqueued)
            for item in data:
                conversion_map.update(item)
        if issubclass(model, Manga):
            conversion_type = "manga"
        elif issubclass(model, Chapter):
            conversion_type = "chapter"
        elif issubclass(model, Group):
            conversion_type = "group"
        elif issubclass(model, Tag):
            conversion_type = "tag"
        else:
            raise ValueError("Model param must be a (sub)class of Manga, Chapter, Group, or Tag.")
        r = await self.request("POST", routes["legacy"], json={"type": conversion_type, "ids": ids})
        json = await r.json()
        r.close()
        for item in json:
            attribs = item["data"]["attributes"]
            conversion_map[attribs["legacyId"]] = model(self, id=attribs["newId"])
        return conversion_map

    async def report_page(self, url: str, success: bool, response_length: int, duration: int, cached: bool):
        """Report a page to the MangaDex@Home network.

        .. versionadded:: 0.4

        .. seealso:: :meth:`.MangadexClient.get_page`, which will automatically call this method for you.

        :param url: The URL of the image.
        :type url: str
        :param success: Whether or not the URL was successfully retrieved.
        :type success: bool
        :param response_length: The length of the response, whether or not it was a success.
        :type response_length: int
        :param duration: The time it took for the request, including downloading the content if it existed,
            **in milliseconds**.
        :type duration: int
        :param cached: Whether or not the request was cached (The ``X-Cache`` header starting with the value ``HIT``).
        :type cached: bool
        """
        r = await self.request(
            "POST",
            routes["report_page"],
            json={
                "url": url,
                "success": success,
                "bytes": response_length,
                "duration": duration,
                "cached": cached,
            },
        )
        r.close()

    async def get_page(self, url: str) -> aiohttp.ClientResponse:
        """A method to download one page of a chapter, using the URLs from :meth:`.pages`. This method is more
        low-level so that it is not necessary to download all pages at once. This method also respects the API rules
        on downloading pages.

        :param url: The URL to download.
        :type url: str
        :raises: :class:`aiohttp.ClientResponseError` if a 4xx or 5xx response code is returned.
        :return: The :class:`aiohttp.ClientResponse` object containing the image.
        :rtype: aiohttp.ClientResponse
        """
        start = datetime.utcnow()
        try:
            r = await self.request("GET", url, retries=1)
            content_length = len(await r.read())
        except Exception:
            success = False
            content_length = 0
            cached = False
            raise
        else:
            success = r.ok and "image" in r.headers.get("Content-Type", "")
            cached = r.headers.get("X-Cache", "").lower().startswith("hit")
            return r
        finally:
            finish = datetime.utcnow()
            time_difference = int((finish - start).total_seconds() * 1000)
            try:
                await asyncio.create_task(
                    self.report_page(url, success, content_length, time_difference, cached)
                )  # NOQA
            except Exception:
                pass

    async def close(self):
        """Close the client.

        .. versionadded:: 0.4
        """
        await self.__aexit__(None, None, None)
