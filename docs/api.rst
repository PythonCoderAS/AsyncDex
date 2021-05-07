AsyncDex API
------------

This page contains all of the classes, attributes, and methods of the various parts of AsyncDex.

Client
++++++

.. autoclass:: asyncdex.MangadexClient
    :members:

Models
++++++

Exceptions
++++++++++

.. autoexception:: asyncdex.exceptions.AsyncDexException
    :members:

.. autoexception:: asyncdex.exceptions.Ratelimit
    :members:

.. autoexception:: asyncdex.exceptions.HTTPException
    :members:

.. autoexception:: asyncdex.exceptions.Unauthorized
    :members:

Enums
+++++

.. autoclass:: asyncdex.enum.Demographic
    :members:

.. autoclass:: asyncdex.enum.MangaStatus
    :members:

.. autoclass:: asyncdex.enum.FollowStatus
    :members:

.. autoclass:: asyncdex.enum.ContentRating
    :members:

.. autoclass:: asyncdex.enum.Visibility
    :members:

.. autoclass:: asyncdex.enum.Relationship
    :members:

Constants
+++++++++

.. autodata:: asyncdex.constants.ratelimit_data
    :no-value:

.. autodata:: asyncdex.constants.routes
    :no-value:

Ratelimit
+++++++++

.. autoclass:: asyncdex.ratelimit.Path
    :members:

.. autoclass:: asyncdex.ratelimit.PathRatelimit
    :members:

.. autoclass:: asyncdex.ratelimit.Ratelimits
    :members:

Misc
++++

.. autofunction:: asyncdex.utils.remove_prefix
