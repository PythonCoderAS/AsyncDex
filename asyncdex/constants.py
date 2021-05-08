from re import compile
from typing import Dict, List

from .ratelimit import Path, PathRatelimit

ratelimit_data: List[PathRatelimit] = [
    PathRatelimit(Path("/account/create", compile(r"/account/create")), 1, 60 * 60),
    PathRatelimit(Path("/account/activate/{code}", compile(r"/account/activate/\S+")), 30, 60 * 60),
    PathRatelimit(Path("/account/activate/resend", compile(r"/account/activate/resend")), 5, 60 * 60),
    PathRatelimit(Path("/account/recover", compile(r"/account/recover")), 5, 60 * 60),
    PathRatelimit(Path("/account/recover/{code}", compile(r"/account/recover/\S+")), 5, 60 * 60),
    PathRatelimit(Path("/auth/login", compile(r"/auth/login")), 30, 30 * 60),
    PathRatelimit(Path("/auth/refresh", compile(r"/auth/refresh")), 30, 30 * 60),
    PathRatelimit(Path("/chapter/{id}/read", compile(r"/chapter/\S+/read")), 300, 10 * 60),
    PathRatelimit(Path("/upload/begin", compile(r"/upload/begin")), 30, 1 * 60),
    PathRatelimit(Path("/upload/{id}", compile(r"/upload/\S+")), 30, 1 * 60),
    PathRatelimit(Path("/upload/{id}/commit", compile(r"/upload/\S+/commit")), 30, 1 * 60),
    PathRatelimit(Path("/chapter/{id}", compile(r"/chapter/\S+"), "PUT"), 10, 1 * 60),
    PathRatelimit(Path("/chapter/{id}", compile(r"/chapter/\S+"), "DELETE"), 10, 1 * 60),
    PathRatelimit(Path("/manga", compile(r"/manga"), "POST"), 10, 60 * 60),
    PathRatelimit(Path("/manga/{id}", compile(r"/manga/\S+"), "PUT"), 10, 1 * 60),
    PathRatelimit(Path("/manga/{id}", compile(r"/manga/\S+"), "DELETE"), 10, 10 * 60),
    PathRatelimit(Path("/group", compile(r"/group"), "POST"), 10, 60 * 60),
    PathRatelimit(Path("/group/{id}", compile(r"/group/\S+"), "PUT"), 10, 1 * 60),
    PathRatelimit(Path("/group/{id}", compile(r"/group/\S+"), "DELETE"), 10, 10 * 60),
    PathRatelimit(Path("/author", compile(r"/author"), "POST"), 10, 60 * 60),
    PathRatelimit(Path("/author/{id}", compile(r"/author/\S+"), "PUT"), 10, 1 * 60),
    PathRatelimit(Path("/author/{id}", compile(r"/author/\S+"), "DELETE"), 10, 10 * 60),
    PathRatelimit(Path("/captcha/solve", compile(r"/captcha/solve"), "POST"), 10, 10 * 60)
]
"""These are the ratelimit rules taken from the API Docs. 

.. note::
    The API rules given here do not reflect all possible API ratelimit rules. The client will automatically ratelimit
    when appropriate headers are sent by the API. Check the latest API rules at
    `the official API documentation <https://api.mangadex.org/docs.html#section/Rating-limits>`_.

.. versionadded:: 0.1
"""

routes: Dict[str, str] = {
    "author": "/author/{id}",
    "author_list": "/author",
    "login": "/auth/login",
    "logout": "/auth/logout",
    "manga": "/manga/{id}",
    "random_manga": "/manga/random",
    "search": "/manga",
    "session_token": "/auth/refresh",
    "tag_list": "/manga/tag",
}
"""The various predefined routes for the client. If the API changes for a given destination, the route can easily
be modified without copy-pasting the route to the functions using it."""
