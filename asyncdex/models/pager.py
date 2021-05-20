import asyncio
from collections import deque
from math import ceil
from typing import Any, AsyncIterator, Generic, MutableMapping, Optional, TYPE_CHECKING, Type, TypeVar

from .abc import GenericModelList, Model, ModelList

if TYPE_CHECKING:
    from ..client import MangadexClient

_ModelT = TypeVar("_ModelT", bound=Model)


class Pager(AsyncIterator[_ModelT], Generic[_ModelT]):
    """A pager object which automatically paginates responses with an offset and limit combo.

    .. versionadded:: 0.3

    :param limit_size: The maximum limit for each request. Defaults to ``100``.
    :type limit_size: int
    """

    url: str
    """The URL to paginate against."""

    model: Type[_ModelT]
    """A subclass of :class:`.Model` to transform the results into."""

    client: "MangadexClient"
    """The client that is associated with the Pager."""

    params: MutableMapping[str, Any]
    """Additional params to include in every request."""

    limit: Optional[int]
    """The Pager will only return up to these many items.
    
    .. versionadded:: 0.4
    """

    returned: int
    """How many items were returned so far.
    
    .. versionadded:: 0.5
    """

    def __init__(
        self,
        url: str,
        model: Type[_ModelT],
        client: "MangadexClient",
        *,
        params: Optional[MutableMapping[str, Any]] = None,
        limit_size: int = 100,
        limit: Optional[int] = None,
    ):
        self.url = url
        self.model = model
        self.client = client
        self.limit = limit
        self.returned = 0
        self.params = params or {}
        self.params.setdefault("offset", 0)
        self.params["limit"] = limit_size
        if self.limit and self.params["limit"] > self.limit:
            self.params["limit"] = self.limit
        self._queue = deque()
        self._reqs = deque()
        self._started_parallel = None
        # A queue that fills after network requests. This is used to only the return the first of a lot of responses
        # on the initial request, and return more items afterwards.
        self._done = False

    def __aiter__(self) -> AsyncIterator[_ModelT]:
        """Return an async iterator (itself)

        :return: The Pager class.
        :rtype: Pager
        """
        return self

    async def _extract_item(self, task: asyncio.Task):
        items = await task
        for item in items:
            self._queue.append(item)

    async def _do_request(self, offset=None):
        offset = offset or self.params["offset"]
        r = await self.client.request("GET", self.url, params={**self.params, "offset": offset})
        if r.status == 204:
            self._done = True
            raise StopAsyncIteration
        json = await r.json()
        r.close()
        if not self._started_parallel:
            self._started_parallel = True
            for item in json["results"]:
                if item:
                    self._queue.append(self.model(self.client, data=item))
            if json["total"] <= self.params["offset"] + self.params["limit"]:
                self._done = True
            else:
                self.params["offset"] += self.params["limit"]
                limit_left = json["total"]
                if self.limit is not None and self.limit > 0:
                    limit_left = self.limit
                extra = int(ceil((limit_left - self.params["limit"]) / self.params["limit"]))
                for i in range(extra):
                    self._reqs.append(
                        asyncio.create_task(self._do_request(offset=self.params["offset"] + self.params["limit"] * i))
                    )
                self._done = True
        else:
            return [self.model(self.client, data=item) for item in json["results"]]

    async def __anext__(self) -> _ModelT:
        """Return a model from the queue. If there are no items remaining, a request is made to fetch the next set of
        items.

        .. versionchanged:: 0.4
            This method will no longer hang to complete all requests.

        .. versionchanged:: 0.5
            This method will fully respect limits even if the API does not.

        :return: The new model.
        :rtype: Model
        """
        if self.limit and self.returned >= self.limit:
            raise StopAsyncIteration
        if len(self._queue) == 0:
            if self._done:
                if len(self._reqs) > 0:
                    await self._extract_item(self._reqs.popleft())
                else:
                    raise StopAsyncIteration
            else:
                await self._do_request(self.params["offset"])
        self.returned += 1
        return self._queue.popleft()

    def __repr__(self) -> str:
        """Provide a string representation of the object.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}(url={self.url!r}, offset={self.params['offset']}, limit={self.params['limit']})"

    async def as_list(self) -> ModelList[_ModelT]:
        """Returns all items in the Pager as a list.

        .. versionchanged:: 0.5
            If :attr:`.model` is :class:`.Manga`, this method will return :class:`.MangaList`. Otherwise, this method
            will return a :class:`.GenericModelList`.

        :return: A :class:`.ModelList` with the total models.

            .. versionchanged:: 0.5
                Prior to 0.5, this method returned a normal :class:`list`.

        :rtype: ModelList
        """
        from .manga import Manga
        from .manga_list import MangaList

        if issubclass(self.model, Manga):
            return MangaList(self.client, entries=[item async for item in self])
        else:
            return GenericModelList([item async for item in self])
