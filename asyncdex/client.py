import asyncio
from datetime import datetime, timedelta
from json import dumps as convert_obj_to_json
from logging import INFO, NullHandler, basicConfig, getLogger
from types import TracebackType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Type, Union, TypeVar

import aiohttp

from .constants import ratelimit_data, routes
from .exceptions import InvalidID, Ratelimit, Unauthorized
from .models.abc import Model
from .models.author import Author
from .models.chapter import Chapter
from .models.group import Group
from .models.manga import Manga
from .models.tag import Tag
from .models.user import User
from .ratelimit import Ratelimits
from .utils import remove_prefix

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

    tag_cache: Dict[str, Tag]
    """A cache of tags. This cache will be used to lower the amount of tag objects, and allows for easily updating 
    the attributes of tags. This cache can be refreshed manually by either calling :meth:`.refresh_tag_cache` or 
    fetching data for any tag object.
    
    .. versionadded:: 0.2
    """

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
        self.tag_cache = {}
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

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Mapping[str, Optional[Union[str, Sequence[str], bool, float]]]] = None,
        json: Any = None,
        with_auth: bool = True,
        retries: int = 3,
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
        :param session_request_kwargs: Optional keyword arguments to pass to :meth:`aiohttp.ClientSession.request`.
        :raises: :class:`.Unauthorized` if the endpoint requires authentication and sufficient parameters for
            authentication were not provided to the client.
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
                else:
                    param_parts.append(f"{name}={convert_obj_to_json(value)}")
            url += "?" + "&".join(param_parts)
        headers = {}
        if with_auth and not self.anonymous_mode:
            if self.session_token is None:
                await self.get_session_token()
            headers["Authorization"] = f"Bearer {self.session_token}"
        if self.sleep_on_ratelimit:
            path_obj = await self.ratelimits.sleep(remove_prefix(self.api_base, url), method)
        else:
            time_to_sleep, path_obj = await self.ratelimits.check(url, method)
            if time_to_sleep > 0 and path_obj:
                raise Ratelimit(path_obj.path.name, path_obj.ratelimit_amount, path_obj.ratelimit_expires)
        if url.startswith(self.api_base):
            # We only want the ratelimit to only apply to the API urls.
            async with self._request_lock:
                # I decided not to throw exceptions for these 1-second ratelimits.
                self._request_count += 1
                time_now = datetime.utcnow()
                time_difference = (time_now - self._request_second_start).total_seconds()
                if time_difference <= 1 and self._request_count >= 5:
                    await asyncio.sleep(1)
                elif time_difference > 1:
                    self._request_count = 0
                    self._request_second_start = time_now
        logger.info("Making %s request to %s", method, url)
        resp = await self.session.request(method, url, headers=headers, json=json, **session_request_kwargs)
        if path_obj:
            path_obj.update(resp)
        do_retry = False
        if resp.status == 401:  # Unauthorized
            if self.session_token:  # Invalid session token
                await self.get_session_token()
                do_retry = True
            elif self.username and self.password:  # Invalid refresh token
                await self.login()
                do_retry = True
            else:
                try:
                    raise Unauthorized(url, resp)
                finally:
                    await resp.release()
        if resp.status == 429:  # Ratelimit error. This should be handled by ratelimits but I'll handle it here as well.
            if resp.headers.get("x-ratelimit-retry-after", ""):
                await asyncio.sleep(
                    (
                        datetime.utcfromtimestamp(int(resp.headers["x-ratelimit-retry-after"])) - datetime.utcnow()
                    ).total_seconds()
                )
            else:
                await asyncio.sleep(1)  # This is probably the result of multiple devices, so sleep for a second. Will
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
        return resp

    async def _one_off(self, method, url, *, params=None, json=None, with_auth=True, retries=3, **kwargs):
        """Use for one-off requests where we do not care about the response."""
        r = await self.request(method, url, params=params, json=json, with_auth=with_auth, retries=retries, **kwargs)
        r.close()

    async def _get_json(self, method, url, *, params=None, json=None, with_auth=True, retries=3, **kwargs):
        """Used for getting the json quickly when we don't care about request codes."""
        r = await self.request(method, url, params=params, json=json, with_auth=with_auth, retries=retries, **kwargs)
        r.raise_for_status()
        json = await r.json()
        r.close()
        return json

    async def get_session_token(self):
        """Get the session token and store it inside the client."""
        if self.refresh_token is None:
            await self.login()
        r = await self.request("POST", routes["session_token"], json={"token": self.refresh_token}, with_auth=False)
        data = await r.json()
        r.close()
        self.session_token = data["token"]["session"]
        self.refresh_token = data["token"]["refresh"]

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
            raise Unauthorized(routes["login"], None)
        r = await self.request(
            "POST", routes["login"], json={"username": self.username, "password": self.password}, with_auth=False
        )
        data = await r.json()
        r.close()
        self.session_token = data["token"]["session"]
        self.refresh_token = data["token"]["refresh"]

    async def logout(self):
        """Log out from the API. If a refresh token exists, calls the logout route on the API. The username and
        password are cleared, and the client is put into anonymous mode."""
        if self.refresh_token or self.session_token:
            (await self.request("POST", routes["logout"])).release()
        self.username = self.password = self.refresh_token = self.session_token = None
        self.anonymous_mode = True

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ):
        """Exit the client and calls :meth:`.logout`. This will also close the underlying session object."""
        await self.logout()
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Provide a string representation of the client.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}(anonymous={self.anonymous_mode!r}, username={self.username!r})"

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

        .. note::
            In order to find a tag by the tag's name, it is recommended to call :meth:`.refresh_tag_cache` and then
            iterate over :attr:`.tag_cache`.

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

    async def _do_batch(self, items: Tuple[Model, ...], route_name: str):
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

        .. versionadded:: 0.2

        :param authors: A tuple of all the authors (and artists) to update.
        :type authors: Tuple[Author, ...]
        """
        await self._do_batch(authors, "author_list")

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

    async def batch_mangas(self, *mangas: Manga):
        """Updates a lot of mangas at once, reducing the time needed to update tens or hundreds of mangas.

        .. versionadded:: 0.2

        :param mangas: A tuple of all the mangas to update.
        :type mangas: Tuple[Manga, ...]
        """
        await self._do_batch(mangas, "search")

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

    async def batch_chapters(self, *chapters: Chapter):
        """Updates a lot of chapters at once, reducing the time needed to update tens or hundreds of chapters.

        .. versionadded:: 0.3

        .. seealso:: :meth:`.ChapterList.get`.

        :param chapters: A tuple of all the chapters to update.
        :type chapters: Tuple[Chapter, ...]
        """
        await self._do_batch(chapters, "chapter_list")

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

        :return: A :class:`.User` object.
        :rtype: User
        """
        r = await self.request("GET", routes["logged_in_user"])
        json = await r.json()
        r.close()
        return User(self, data=json)

    async def ping(self):
        """Ping the server. This will throw an error if there is any error in making connections, whether with the
        client or the server.

        .. versionadded:: 0.3
        """
        return await self._one_off("GET", routes["ping"])

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

    async def batch_groups(self, *groups: Group):
        """Updates a lot of groups at once, reducing the time needed to update tens or hundreds of groups.

        .. versionadded:: 0.3

        :param groups: A tuple of all the groups to update.
        :type groups: Tuple[Group, ...]
        """
        await self._do_batch(groups, "group_list")
