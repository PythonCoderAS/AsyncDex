AsyncDex API
------------

This page contains all of the classes, attributes, and methods of the various parts of AsyncDex.

Client
++++++

.. autoclass:: asyncdex.MangadexClient
    :members:
    :special-members: __aenter__, __aexit__, __repr__

Models
++++++

.. autoclass:: asyncdex.models.abc.Model
    :members:
    :special-members: __str__, __eq__, __ne__, __hash__, __repr__

.. autoclass:: asyncdex.models.Author
    :members:
    :inherited-members:
    :special-members: __str__, __eq__, __ne__, __hash__

.. autoclass:: asyncdex.models.Chapter
    :members:
    :inherited-members:
    :special-members: __lt__, __le__, __gt__, __ge__, __str__, __eq__, __ne__, __hash__

.. autoclass:: asyncdex.models.Group
    :members:
    :inherited-members:
    :special-members: __lt__, __le__, __gt__, __ge__, __str__, __eq__, __ne__, __hash__

.. autoclass:: asyncdex.models.Manga
    :members:
    :inherited-members:
    :special-members: __lt__, __le__, __gt__, __ge__, __str__, __eq__, __ne__, __hash__

.. autoclass:: asyncdex.models.Tag
    :members:
    :inherited-members:
    :special-members: __str__, __eq__, __ne__, __hash__

.. autoclass:: asyncdex.models.User
    :members:
    :inherited-members:
    :special-members: __str__, __eq__, __ne__, __hash__

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

.. autoexception:: asyncdex.exceptions.Missing
    :members:

.. autoexception:: asyncdex.exceptions.InvalidID
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

.. autoclass:: asyncdex.enum.DuplicateResolutionAlgorithm
    :members:

Constants
+++++++++

.. autodata:: asyncdex.constants.invalid_folder_name_regex
    :no-value:

.. autodata:: asyncdex.constants.ratelimit_data
    :no-value:

.. autodata:: asyncdex.constants.routes
    :no-value:

Ratelimit
+++++++++

.. autoclass:: asyncdex.ratelimit.Path
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__

.. autoclass:: asyncdex.ratelimit.PathRatelimit
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__


.. autoclass:: asyncdex.ratelimit.Ratelimits
    :members:
    :special-members: __repr__

Misc
++++

.. autofunction:: asyncdex.utils.remove_prefix

.. autoclass:: asyncdex.utils.AttrDict
    :members:
    :special-members: __getattr__, __setattr__, __repr__

.. autoclass:: asyncdex.utils.DefaultAttrDict
    :members:
    :special-members: __getattr__, __setattr__, __repr__, __missing__

.. autofunction:: asyncdex.utils.copy_key_to_attribute

.. autofunction:: asyncdex.utils.parse_relationships

.. autoclass:: asyncdex.models.mixins.DatetimeMixin
    :members:
    :special-members: __lt__, __le__, __gt__, __ge__

.. autoclass:: asyncdex.models.title.TitleList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.ChapterList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.pager.Pager
    :members:
    :special-members: __repr__, __aiter__, __anext__

.. autoclass:: asyncdex.utils.Interval
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__

.. autoclass:: asyncdex.utils.InclusionExclusionPair
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__
