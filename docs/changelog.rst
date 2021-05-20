Changelog
#########

v0.5
----

Added
+++++

* :meth:`.ChapterList.filter` has two new parameters: ``read`` and ``volumes``.
* :class:`.VolumeAggregate`
* :class:`.MangaAggregate`
* :meth:`.TagDict.__repr__`
* :meth:`.group_by_volumes`
* :meth:`.group_by_numbers`
* :meth:`.group_by_volume_and_chapters`
* :meth:`.calculate_aggregate`
* :meth:`.languages`
* :meth:`.aggregate`
* :meth:`.mark_read`
* :meth:`.mark_unread`
* :meth:`.toggle_read`
* :meth:`.Chapter.get_read`
* :meth:`.ChapterList.get_read`
* :meth:`.id_map`
* :meth:`.batch_manga_read`
* :meth:`.ChapterList.get` has two new parameters: ``order`` and ``limit``.
* :meth:`.get_new`
* :meth:`.ClientUser.chapter_chapters`
* :class:`.MangaFeedListOrder`
* :meth:`.ClientUser.manga`
* :class:`.ModelList`
* :class:`.GenericModelList`
* :meth:`.ChapterList.fetch_all`
* :attr:`.Chapter.read`
* :attr:`.Manga.reading_status`
* :meth:`.Manga.get_reading_status`
* :meth:`.Manga.set_reading_status`
* :class:`.MangaList`
* :class:`.ClientUser`
* :attr:`.MangadexClient.user`
* :class:`.PermissionMismatch`
* Added permission checks to various methods.
* :class:`.CustomList`
* :meth:`.get_list`
* :class:`.MangaLinks`
* :meth:`.Manga.__getattr__`
* :meth:`.Manga.update`
* :meth:`.Manga.delete`
* :meth:`.add_to_list`
* :meth:`.remove_from_list`
* :meth:`.follow`
* :meth:`.unfollow`
* :meth:`.TitleList.parts`
* :meth:`.create_manga`

Changed
+++++++

* Attributes converted to a :class:`.GenericModelList`:
    * :attr:`.Chapter.groups`
    * :attr:`.Group.members`
    * :attr:`.Group.chapters`
    * :attr:`.Manga.tags`
    * :attr:`.Manga.authors`
    * :attr:`.Manga.artists`
    * :attr:`.User.chapters`
* :class:`.Pager` will return :class:`.GenericModelList`\ s (or :class:`.MangaList` if parameter ``model`` is :class:`.Manga`).
* The key in the dictionary returned by :meth:`.TagDict.groups` is now a :class:`.GenericModelList`.
* :meth:`.parse_relationships` will now set :class:`.GenericModelList`\ s instead of normal lists.


Deprecated
++++++++++

* :meth:`.MangadexClient.logged_in_user`
* :meth:`.Chapter.get_page`
* Parameter ``locales`` for :meth:`.ChapterList.get`
* Parameter ``locales`` for :meth:`.ChapterList.filter`

Fixed
+++++

* Fixed a bug in :class:`.Pager` where more items would be returned than the given limit.
* Fixed a bug in :meth:`.PathRatelimit.update` that prevented a ratelimit from being applied correctly.
* Fixed a bug in :meth:`.User.__eq__` that returned False when the ClientUser was the same user as a given user.
* Fixed a bug in :meth:`.Manga.parse` where chapters without a description would cause an exception to be raised.

v0.4
----

Added
+++++

* :func:`.return_date_string`
* :meth:`.download_all`
* :attr:`.Pager.limit` to limit total responses,
* :meth:`.Pager.as_list`
* :attr:`.Tag.descriptions`
* :attr:`.Tag.group`
* :class:`.TagDict`
* Allow the creation of :class:`.User` objects if the ID is in the base data dictionary.
* :attr:`.Demographic.NONE`
* :class:`.OrderDirection`
* :class:`.TagMode`
* :class:`.AuthorListOrder`
* :class:`.ChapterListOrder`
* :class:`.GroupListOrder`
* :class:`.MangaListOrder`
* Methods added to :class:`.MangadexClient`:
    * :meth:`.get_groups`
    * :meth:`.get_chapters`
    * :meth:`.get_authors`
    * :meth:`.get_mangas`
    * :meth:`.report_page`
    * :meth:`.MangadexClient.close`

Changed
+++++++

* Changed :meth:`.download_chapter` so that directories are not created until all pages are retrieved.
* Moved :meth:`.Chapter.get_page` to :meth:`.MangadexClient.get_page`.

Fixed
+++++

* Fixed :meth:`.Pager.__anext__` so it does not need to complete all requests before returning the first batch of statements. This will drastically improve performance if all items aren't needed immediately (such as making further requests with returned data).
* Fixed a bug where the chapter list would clear itself when filtered.
* Fixed a bug where :meth:`.download_chapter` would not try again due to certain errors such as establishing a connection.
* Fixed :meth:`.Chapter.pages` so it respects the ``forcePort443`` parameter.


v0.3
----

Added
+++++

* Added a ratelimit on the `/at-home/server/{id}` path to match the 5.0.2 release of the MD API.
* Added a global ratelimit for 5 req/s to match the ratelimit set by the MD API.
* :class:`.DuplicateResolutionAlgorithm`
* :class:`.Chapter`
* :class:`.ChapterList`
* :class:`.Group`
* :attr:`.Manga.chapters`
* :class:`.Pager`
* :class:`.User`
* Methods added to :class:`.MangadexClient`:
    * :meth:`~.get_chapter`
    * :meth:`~.batch_chapters`
    * :meth:`~.get_user`
    * :meth:`~.logged_in_user`
    * :meth:`~.ping`
    * :meth:`~.convert_legacy`
    * :meth:`~.get_group`
    * :meth:`~.batch_groups`
* :meth:`.AttrDict.first` and :meth:`.DefaultAttrDict.first`
* :class:`.Interval`
* :class:`.InclusionExclusionPair`


Changed
+++++++

* :attr:`.Manga.last_volume` and :attr:`.Manga.last_chapter` both are now Strings.
* Made all of the ``batch_*`` methods on the Client class parallel. This will speed up batch requests over the size of 100 items fivefold.


Fixed
+++++

* :attr:`.Manga.last_chapter` did not account for floating point variables.
* Changed :meth:`.Model.__repr__` to properly show the delimiters for strings.
* :meth:`.MangadexClient.__aexit__` will now close the underlying session object.
* Fixed a bug in :meth:`.Client.request` that prevented the use of non-string and non-iterable objects such as integers and floats.
* Added a client-side fix for the incorrect spelling of the word ``hiatus`` on the MangaDex API.
* Fixed a typo on :attr:`.Demographic.JOSEI` where the term "josei" was actually spelled "josel".
* Added a message to :class:`.Unauthorized`.
* Fixed a bunch of places where requests are not properly closed.
* Changed the value of ``MangaStatus.ABANDONED`` to match new API specifications.
* Fixed a bug in the retry mechanism of :meth:`.Client.request` that added the parameters for a second time.

v0.2
----

Added
+++++

* The 6 enums:
    #. :class:`.Demographic`
    #. :class:`.MangaStatus`
    #. :class:`.FollowStatus`
    #. :class:`.ContentRating`
    #. :class:`.Visibility`
    #. :class:`.Relationship`
* :class:`.Missing`
* :class:`.InvalidID`
* Models:
    * :class:`.Model`
    * :class:`.Manga`
    * :class:`.Tag`
    * :class:`.Author`
* :attr:`~.tag_cache` inside of :class:`.MangadexClient`
* Methods to :class:`.MangadexClient`:
    * :meth:`~.refresh_tag_cache`
    * :meth:`~.get_tag`
    * :meth:`~.get_manga`
    * :meth:`~.random_manga`
    * :meth:`~.batch_authors`
    * :meth:`~.get_author`
    * :meth:`~.batch_mangas`
* :class:`.DatetimeMixin`
* :class:`.TitleList`
* :class:`.AttrDict`
* :class:`.DefaultAttrDict`
* :func:`.copy_key_to_attribute`
* :func:`.parse_relationships`

v0.1
----

The initial release of AsyncDex.
