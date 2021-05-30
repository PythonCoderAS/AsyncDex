from datetime import datetime
from os.path import abspath, join
from typing import Optional

import pytest

from asyncdex import Author, Chapter, Group, Manga, MangadexClient, Unauthorized


class TestConstructor:
    @pytest.mark.asyncio
    async def test_anonymous(self):
        client = MangadexClient()
        assert client.anonymous_mode
        assert not client.username
        assert not client.password
        assert not client.refresh_token
        assert not client.session_token
        await client.close()

    @pytest.mark.asyncio
    async def test_not_anonymous_username_password(self):
        client = MangadexClient(username="Test", password="Test")
        assert not client.anonymous_mode
        assert client.username
        assert client.password
        assert not client.refresh_token
        assert not client.session_token
        await client.close()

    @pytest.mark.asyncio
    async def test_not_anonymous_refresh_token(self):
        client = MangadexClient(refresh_token="Test")
        assert not client.anonymous_mode
        assert not client.username
        assert not client.password
        assert client.refresh_token
        assert not client.session_token
        await client.close()

    @pytest.mark.asyncio
    async def test_username_password_and_refresh_token(self):
        client = MangadexClient(username="Test", password="Test", refresh_token="Test")
        assert not client.anonymous_mode
        assert client.username
        assert client.password
        assert client.refresh_token
        assert not client.session_token
        await client.close()

    def test_username_and_password(self):
        with pytest.raises(ValueError):
            MangadexClient(username="Test")
        with pytest.raises(ValueError):
            MangadexClient(password="Test")

    @pytest.mark.asyncio
    async def test_anonymous_option(self):
        client = MangadexClient(username="Test", password="Test", refresh_token="Test", anonymous=True)
        assert client.anonymous_mode
        assert not client.username
        assert not client.password
        assert not client.refresh_token
        assert not client.session_token
        await client.close()

class TestDunder:


    @pytest.mark.asyncio
    async def test_async_with(self):
        async with MangadexClient(username="Test", password="Test") as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert not client.refresh_token
            assert not client.session_token
        async with MangadexClient() as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_repr(self):
        async with MangadexClient(username="Test", password="Test") as client:
            assert repr(client) == "MangadexClient(anonymous=False, username='Test')"


class TestAuth:

    @pytest.mark.asyncio
    async def test_unauthorized_exception(self):
        async with MangadexClient() as client:
            with pytest.raises(Unauthorized):
                client.raise_exception_if_not_authenticated("GET", "TEST")

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_login(self, username, password):
        async with MangadexClient(username=username, password=password) as client:
            await client.login()
            assert client.session_token
            assert client.user.id != "client-user"
            assert client.user.permissions == ['user.list',
                                               'manga.view',
                                               'chapter.view',
                                               'author.view',
                                               'scanlation_group.view',
                                               'cover.view',
                                               'manga.list',
                                               'chapter.list',
                                               'author.list',
                                               'scanlation_group.list',
                                               'cover.list']

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_refresh_token(self, refresh_token):
        async with MangadexClient(refresh_token=refresh_token) as client:
            await client.get_session_token()
            assert client.session_token
            assert client.user.id != "client-user"
            assert client.user.permissions == ['user.list',
                                               'manga.view',
                                               'chapter.view',
                                               'author.view',
                                               'scanlation_group.view',
                                               'cover.view',
                                               'manga.list',
                                               'chapter.list',
                                               'author.list',
                                               'scanlation_group.list',
                                               'cover.list']

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_refresh_token_from_username_and_password(self, username, password):
        async with MangadexClient(username=username, password=password) as client:
            await client.login()
            assert client.session_token
            assert client.user.id != "client-user"
            assert client.user.permissions == ['user.list',
                                               'manga.view',
                                               'chapter.view',
                                               'author.view',
                                               'scanlation_group.view',
                                               'cover.view',
                                               'manga.list',
                                               'chapter.list',
                                               'author.list',
                                               'scanlation_group.list',
                                               'cover.list']
            client.session_token = None
            assert not client.session_token
            await client.get_session_token()
            assert client.session_token

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_auto_expire_session_token(self, username, password):
        async with MangadexClient(username=username, password=password) as client:
            await client.login()
            client._session_token_acquired = datetime(2000, 1, 1)
            assert not client.session_token
            await client.get_session_token()
            assert client.session_token
            assert client._session_token_acquired != datetime(2000, 1, 1)

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_auto_login(self, username, password):
        async with MangadexClient(username=username, password=password) as client:
            await client.ping()
            assert client.session_token
            assert client.user.id != "client-user"
            assert client.user.permissions == ['user.list',
                                               'manga.view',
                                               'chapter.view',
                                               'author.view',
                                               'scanlation_group.view',
                                               'cover.view',
                                               'manga.list',
                                               'chapter.list',
                                               'author.list',
                                               'scanlation_group.list',
                                               'cover.list']

    @pytest.mark.asyncio
    @pytest.mark.vcr()
    async def test_auto_session_token(self, refresh_token):
        async with MangadexClient(refresh_token=refresh_token) as client:
            await client.ping()
            assert client.session_token
            assert client.user.id != "client-user"
            assert client.user.permissions == ['user.list',
                                               'manga.view',
                                               'chapter.view',
                                               'author.view',
                                               'scanlation_group.view',
                                               'cover.view',
                                               'manga.list',
                                               'chapter.list',
                                               'author.list',
                                               'scanlation_group.list',
                                               'cover.list']


class TestGetIndividual:
    @pytest.mark.asyncio
    async def test_get_manga(self):
        async with MangadexClient() as client:
            manga = client.get_manga("Test")
            assert isinstance(manga, Manga)


    @pytest.mark.asyncio
    async def test_get_author(self):
        async with MangadexClient() as client:
            author = client.get_author("Test")
            assert isinstance(author, Author)


    @pytest.mark.asyncio
    async def test_get_group(self):
        async with MangadexClient() as client:
            group = client.get_group("Test")
            assert isinstance(group, Group)


    @pytest.mark.asyncio
    async def test_get_chapter(self):
        async with MangadexClient() as client:
            chapter = client.get_chapter("Test")
            assert isinstance(chapter, Chapter)


class TestEnvVars:

    @pytest.mark.asyncio
    async def test_init_env_var(self, monkeypatch):
        monkeypatch.setenv("asyncdex_username", "test")
        monkeypatch.setenv("asyncdex_password", "test")
        monkeypatch.setenv("asyncdex_refresh_token", "test")
        async with MangadexClient.from_environment_variables() as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_init_env_var_alternate_names(self, monkeypatch):
        monkeypatch.setenv("au", "test")
        monkeypatch.setenv("ap", "test")
        monkeypatch.setenv("art", "test")
        async with MangadexClient.from_environment_variables(
            username_variable_name="au", password_variable_name="ap", refresh_token_variable_name="art"
        ) as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_init_env_var_anonymous(self, monkeypatch):
        monkeypatch.delenv("asyncdex_username", raising=False)
        monkeypatch.delenv("asyncdex_password", raising=False)
        monkeypatch.delenv("asyncdex_refresh_token", raising=False)
        async with MangadexClient.from_environment_variables() as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_init_env_var_boolean(self, monkeypatch):
        monkeypatch.setenv("asyncdex_username", "test")
        monkeypatch.setenv("asyncdex_password", "test")
        monkeypatch.setenv("asyncdex_refresh_token", "test")
        monkeypatch.setenv("asyncdex_anonymous", "true")
        async with MangadexClient.from_environment_variables() as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_init_env_var_username_password_only(self, monkeypatch):
        monkeypatch.setenv("asyncdex_username", "test")
        monkeypatch.setenv("asyncdex_password", "test")
        monkeypatch.delenv("asyncdex_refresh_token", raising=False)
        async with MangadexClient.from_environment_variables() as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert not client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_init_env_var_refresh_token_only(self, monkeypatch):
        monkeypatch.delenv("asyncdex_username", raising=False)
        monkeypatch.delenv("asyncdex_password", raising=False)
        monkeypatch.setenv("asyncdex_refresh_token", "test")
        async with MangadexClient.from_environment_variables() as client:
            assert not client.anonymous_mode
            assert not client.username
            assert not client.password
            assert client.refresh_token
            assert not client.session_token

class TestConfig:
    
    @property
    def file_path(self):
        return abspath(join(__file__, "..", "data", "test.ini"))

    @pytest.mark.asyncio
    async def test_config_file(self):
        async with MangadexClient.from_config(self.file_path) as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_config_file_custom_name(self):
        async with MangadexClient.from_config(self.file_path, section_name="asyncdex_custom_name") as \
                client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_config_file_anonymous(self):
        async with MangadexClient.from_config(self.file_path, section_name="asyncdex_anonymous") as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token


    @pytest.mark.asyncio
    async def test_config_file_anonymous_mode(self):
        async with MangadexClient.from_config(self.file_path, section_name="asyncdex_anonymous_mode") as \
                client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_config_file_username_password_only(self):
        async with MangadexClient.from_config(self.file_path,
                                              section_name="asyncdex_username_and_password_only") as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_config_file_refresh_token_only(self):
        async with MangadexClient.from_config(self.file_path,
                                              section_name="asyncdex_refresh_token_only") as client:
            assert not client.anonymous_mode
            assert not client.username
            assert not client.password
            assert client.refresh_token
            assert not client.session_token

class TestJSON:
    
    def file_path(self, suffix: Optional[str] = None):
        filename = "test"
        if suffix:
            filename += "_" + suffix
        filename += ".json"
        return abspath(join(__file__, "..", "data", "json", filename))

    @pytest.mark.asyncio
    async def test_json(self):
        async with MangadexClient.from_json(self.file_path()) as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_json_anonymous(self):
        async with MangadexClient.from_json(self.file_path("anonymous")) as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_json_anonymous_mode(self):
        async with MangadexClient.from_json(self.file_path("anonymous_mode")) as client:
            assert client.anonymous_mode
            assert not client.username
            assert not client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_json_username_password_only(self):
        async with MangadexClient.from_json(self.file_path("username_password")) as client:
            assert not client.anonymous_mode
            assert client.username
            assert client.password
            assert not client.refresh_token
            assert not client.session_token

    @pytest.mark.asyncio
    async def test_json_refresh_token_only(self):
        async with MangadexClient.from_json(self.file_path("refresh_token")) as client:
            assert not client.anonymous_mode
            assert not client.username
            assert not client.password
            assert client.refresh_token
            assert not client.session_token
