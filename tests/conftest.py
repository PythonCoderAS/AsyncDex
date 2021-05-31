import logging
import os
from typing import Any, Dict, Union

import pytest

logging.getLogger("vcr").setLevel(logging.WARNING)


def before_record_response(response: Dict[str, Union[Dict[str, Any], Any]]):
    if response["url"] in ["https://api.mangadex.org/auth/login", "https://api.mangadex.org/auth/refresh"]:
        response["body"]["string"] = '{"result":"ok","token":{"session":"session_token","refresh":"refresh"}}'
    return response


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "before_record_response": before_record_response,
        "filter_headers": [("authorization", "AUTHORIZATION")],
        "filter_post_data_parameters": [
            ("username", "USERNAME"),
            ("password", "PASSWORD"),
            ("token", "REFRESH_TOKEN"),
        ],
    }


@pytest.fixture
def username():
    return os.environ.get("asyncdex_username", "user")


@pytest.fixture
def password():
    return os.environ.get("asyncdex_password", "pass")


@pytest.fixture
def refresh_token():
    return os.environ.get("asyncdex_refresh_token", "refresh")
