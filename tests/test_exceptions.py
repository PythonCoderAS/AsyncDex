import re
from datetime import datetime

import pytest
from aiohttp import ClientResponseError

from asyncdex import AsyncDexException, HTTPException, MangadexClient, Ratelimit
from asyncdex.constants import routes


class TestAsyncDexException:
    def test_subclass(self):
        assert issubclass(AsyncDexException, Exception)
        exc = AsyncDexException()
        assert isinstance(exc, Exception)
        with pytest.raises(AsyncDexException):
            raise exc
        with pytest.raises(Exception):
            raise exc

    def test_message(self):
        with pytest.raises(AsyncDexException) as exc:
            raise AsyncDexException("test")
        assert str(exc.value) == "test"


class TestRatelimit:
    def test_subclass(self):
        assert issubclass(Ratelimit, AsyncDexException)
        exc = Ratelimit("a", 1, datetime.utcnow())
        assert isinstance(exc, AsyncDexException)
        with pytest.raises(Ratelimit):
            raise exc
        with pytest.raises(AsyncDexException):
            raise exc

    def test_message(self):
        with pytest.raises(Ratelimit) as exc:
            raise Ratelimit("/test", 1, datetime.fromtimestamp(int(datetime.utcnow().timestamp()) + 100))
        assert re.match(r"Ratelimited for 99.\d{3} seconds on /test", str(exc.value))

    def test_attrs(self):
        now = datetime.utcnow()
        exc = Ratelimit("a", 1, now)
        assert exc.path == "a"
        assert exc.ratelimit_amount == 1
        assert exc.ratelimit_expires == now


class TestHTTPException:
    def test_subclass(self):
        assert issubclass(HTTPException, AsyncDexException)
        assert issubclass(HTTPException, ClientResponseError)
        exc = HTTPException("a", "a", None)
        assert isinstance(exc, AsyncDexException)
        assert isinstance(exc, ClientResponseError)
        with pytest.raises(HTTPException):
            raise exc
        with pytest.raises(AsyncDexException):
            raise exc
        with pytest.raises(ClientResponseError):
            raise exc

    def test_message_no_response(self):
        with pytest.raises(HTTPException) as exc:
            raise HTTPException("GET", "/test", None)
        assert str(exc.value) == "HTTP Error on GET for /test."

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_message_response(self):
        async with MangadexClient() as client:
            with pytest.raises(HTTPException) as exc:
                await client.request("GET", "/fakepath" * 1000)
        assert (
            str(exc.value) == "HTTP 414: HTTP Error on GET for "
            "https://api.mangadex.org/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath/fakepath"
            "/fakepath"
            "/fakepath/fakepath/fakepath."
        )

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_message_response_json(self):
        async with MangadexClient() as client:
            r = await client.request("get", routes["ping"])
            with pytest.raises(HTTPException) as exc:
                raise HTTPException(
                    "GET", routes["ping"], response=r, json={"errors": [{"title": "Test", "detail": "This is a test."}]}
                )
            assert str(exc.value) == "HTTP 200: Test: This is a test."

    def test_message_no_response_json(self):
        with pytest.raises(HTTPException) as exc:
            raise HTTPException(
                "GET", routes["ping"], response=None, json={"errors": [{"title": "Test", "detail": "This is a test."}]}
            )
        assert str(exc.value) == "Test: This is a test."

    def test_message_no_response_json_context(self):
        with pytest.raises(HTTPException) as exc:
            raise HTTPException(
                "GET",
                routes["ping"],
                response=None,
                json={"errors": [{"title": "Test", "detail": "This is a test.", "context": {"test": 1}}]},
            )
        assert str(exc.value) == "Test: This is a test. ({'test': 1})"

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_message_response_json_context(self):
        async with MangadexClient() as client:
            r = await client.request("get", routes["ping"])
            with pytest.raises(HTTPException) as exc:
                raise HTTPException(
                    "GET",
                    routes["ping"],
                    response=r,
                    json={"errors": [{"title": "Test", "detail": "This is a test.", "context": {"test": 1}}]},
                )
            assert str(exc.value) == "HTTP 200: Test: This is a test. ({'test': 1})"

    def test_message_custom_no_locals(self):
        with pytest.raises(HTTPException) as exc:
            raise HTTPException("None", "None", None, msg="Test")
        assert str(exc.value) == "Test"

    def test_message_custom_locals(self):
        with pytest.raises(HTTPException) as exc:
            raise HTTPException("None", "None", None, msg="{method}: {path}")
        assert str(exc.value) == "None: None"

    def test_message_no_locals(self):
        with pytest.raises(KeyError):
            HTTPException("None", "None", None, msg="{i_do_not_exist}")
