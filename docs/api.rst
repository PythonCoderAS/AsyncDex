AsyncDex API
------------

This page contains all of the classes, attributes, and methods of the various parts of AsyncDex.

Client
++++++

.. autoclass:: asyncdex.MangadexClient
    :members:
    :special-members: __aenter__, __aexit__, __repr__

ClientUser
..........

.. autoclass:: asyncdex.models.client_user.ClientUser
    :members:
    :inherited-members:
    :special-members: __str__, __eq__, __ne__, __hash__

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

.. autoexception:: asyncdex.exceptions.HTTPException
    :members:

.. autoexception:: asyncdex.exceptions.InvalidID
    :members:

.. autoexception:: asyncdex.exceptions.Missing
    :members:

.. autoexception:: asyncdex.exceptions.PermissionMismatch
    :members:

.. autoexception:: asyncdex.exceptions.Ratelimit
    :members:

.. autoexception:: asyncdex.exceptions.Unauthorized
    :members:


Enums
+++++

MangaDex Enums
..............

.. autoclass:: asyncdex.enum.ContentRating
    :members:

.. autoclass:: asyncdex.enum.Demographic
    :members:

.. autoclass:: asyncdex.enum.FollowStatus
    :members:

.. autoclass:: asyncdex.enum.MangaStatus
    :members:

.. autoclass:: asyncdex.enum.Visibility
    :members:

.. autoclass:: asyncdex.enum.Relationship
    :members:

Filtering
.........

.. autoclass:: asyncdex.enum.DuplicateResolutionAlgorithm
    :members:

Sorting & Searching
...................

.. autoclass:: asyncdex.enum.OrderDirection
    :members:

.. autoclass:: asyncdex.enum.TagMode
    :members:

Constants
+++++++++

.. autodata:: asyncdex.constants.invalid_folder_name_regex
    :no-value:

.. autodata:: asyncdex.constants.ratelimit_data
    :no-value:

.. autodata:: asyncdex.constants.routes
    :no-value:

Misc
++++

Aggregates
..........

.. autoclass:: asyncdex.models.aggregate.MangaAggregate
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.aggregate.VolumeAggregate
    :members:
    :special-members: __repr__

Attribute Dictionaries
......................
.. autoclass:: asyncdex.utils.AttrDict
    :members:
    :special-members: __getattr__, __setattr__, __repr__

.. autoclass:: asyncdex.utils.DefaultAttrDict
    :members:
    :special-members: __getattr__, __setattr__, __repr__, __missing__

Filtering Utilities
...................

.. autoclass:: asyncdex.utils.InclusionExclusionPair
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__

.. autoclass:: asyncdex.utils.Interval
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__

List Orders
...........

.. autoclass:: asyncdex.list_orders.AuthorListOrder
    :members:

.. autoclass:: asyncdex.list_orders.ChapterListOrder
    :members:

.. autoclass:: asyncdex.list_orders.GroupListOrder
    :members:

.. autoclass:: asyncdex.list_orders.MangaListOrder
    :members:

.. autoclass:: asyncdex.list_orders.MangaFeedListOrder
    :members:

Model Containers
................

.. autoclass:: asyncdex.models.abc.ModelList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.abc.GenericModelList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.title.TitleList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.ChapterList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.MangaList
    :members:
    :special-members: __repr__

.. autoclass:: asyncdex.models.tag.TagDict
    :members:
    :special-members: __repr__

Model Mixins
............

.. autoclass:: asyncdex.models.mixins.DatetimeMixin
    :members:
    :special-members: __lt__, __le__, __gt__, __ge__

Pager
.....

.. autoclass:: asyncdex.models.pager.Pager
    :members:
    :special-members: __repr__, __aiter__, __anext__

Ratelimit
.........

.. autoclass:: asyncdex.ratelimit.Path
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__, __hash__

.. autoclass:: asyncdex.ratelimit.PathRatelimit
    :members:
    :special-members: __eq__, __ne__, __le__, __lt__, __gt__, __ge__


.. autoclass:: asyncdex.ratelimit.Ratelimits
    :members:
    :special-members: __repr__

Misc Functions
..............

.. autofunction:: asyncdex.utils.copy_key_to_attribute

.. autofunction:: asyncdex.utils.parse_relationships

.. autofunction:: asyncdex.utils.remove_prefix

.. autofunction:: asyncdex.utils.return_date_string

References
++++++++++

* .. [#V506_CHANGELOG] This parameter is undocumented in the API as of May 16, 2021. The inclusion of this parameter can be found in the changelog of the v5.0.6 release of the API, found in the `MangaDex Discord <https://discord.com/channels/403905762268545024/839817812012826644/843097446384533544>`_.
