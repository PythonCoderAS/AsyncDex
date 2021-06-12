Changelog
#########

v1.1
----

Added
+++++

* :class:`.UserFollowsMangaFeedListOrder`
* Parameter ``add_includes`` to :meth:`.request` to automatically add the reference expansion parameters in as long as the user has the permissions required.
* :data:`.permission_model_mapping`
* Methods that now expand references:
    * :meth:`.random_manga`
    * :meth:`.Author.fetch`
    * :meth:`.Chapter.fetch`
    * :meth:`.CoverArt.fetch`
    * :meth:`.CustomList.fetch`
    * :meth:`.Group.fetch`
    * :meth:`.Manga.fetch`
    * :meth:`.User.fetch`
    * :meth:`.batch_authors`
    * :meth:`.batch_chapters`
    * :meth:`.batch_covers`
    * :meth:`.batch_groups`
    * :meth:`.batch_mangas`
    * :meth:`.get_authors`
    * :meth:`.get_chapters`
    * :meth:`.MangadexClient.get_covers`
    * :meth:`.get_groups`
    * :meth:`.get_mangas`
    * :meth:`.ChapterList.get`
    * :meth:`.ClientUser.groups`
    * :meth:`.ClientUser.lists`
    * :meth:`.ClientUser.manga`
    * :meth:`.ClientUser.manga_chapters`
    * :meth:`.ClientUser.users`
    * :meth:`.CustomList.manga_chapters`

Changed
+++++++

* :meth:`.CustomList.fetch` no longer requires authentication if the list is a public list.
* The :attr:`.CoverArt.manga` attribute will be assigned to the manga that owns the cover art, if it is created by :meth:`.Manga.fetch`.
* Parameters ``volume`` and ``chapter_number`` of :meth:`.get_chapters` now accept a list of strings to select multiple volume/chapters.
* :func:`.parse_relationships` will now make objects using the reference expansion data.


Fixed
+++++

* :class:`.VolumeAggregate` will correctly return values for null chapters.
* :class:`.MangaAggregate` will correctly return values for null volumes.
* Fixed an issue where CoverArt instances did not correctly assign attributes.

v1.0
----

Added
+++++

* :attr:`.Relationship.COVER_ART`
* :class:`.CoverArt`
* :meth:`.from_environment_variables`
* :meth:`.from_config`
* :meth:`.from_json`
* :meth:`.get_cover`
* :meth:`.batch_covers`
* :attr:`.Manga.cover`
* :meth:`MangadexClient.get_covers`
* :meth:`.create_cover`
* :class:`.CoverListOrder`
* :meth:`.parse_relationships` can now parse :class:`.CoverArt` models.
* :class:`.CoverList`
* :attr:`.Manga.covers`
* :attr:`.ContentRating.NO_RATING`
* :meth:`.MangaList.get_covers`

Changed
+++++++

* :class:`.Pager` will now throw exceptions when it is given too many parameters.
* :attr:`.HTTPException.response` may be ``None``.
* :class:`.HTTPException` is now a subclass of :class:`aiohttp.ClientResponseError`.
* :meth:`.request` will raise :class:`.HTTPException`.
* :meth:`.ModelList.fetch_all` will use :meth:`.batch_covers`.

Deprecated
++++++++++

* :attr:`.Group.chapters`
* :attr:`.User.chapters`

Fixed
+++++

* Renamed ``locales`` to ``translatedLanguage``.
* Added the version to :meth:`.Group.update`.
* Fixed a bug in :meth:`.Pager.__anext__` that threw Exceptions if the server response was empty.
* Fixed a bug where list orders were not being correctly applied.
* Fixed a bug where trying to log in without a username and password but with a refresh token would make a network request.
* Fixed an erroneous ``await`` call that would very rarely lead to exceptions.
* Fixed a bug where a new refresh token would be fetched if the session token was ``None``.
* Fixed a bug where invalid session/refresh tokens would cause an infinite loop.
* Fixed a bug where the refresh token and session token being invalid would cause a loop and result in an exception being raised.
* Fixed a bug in :class:`.AttrDict` where :func:`hasattr` and :func:`getattr` would raise KeyErrors.

Removed
+++++++

* Method ``Chapter.get_page()``
* Parameter ``locales`` in :meth:`.ChapterList.get` and :meth:`.ChapterList.filter`
* Attribute ``Manga.anilist_id``
* Attribute ``Manga.animeplanet_id``
* Attribute ``Manga.bookwalker_id``
* Attribute ``Manga.mangaupdates_id``
* Attribute ``Manga.novelupdates_id``
* Attribute ``Manga.kitsu_id``
* Attribute ``Manga.amazon_id``
* Attribute ``Manga.cdjapan_id``
* Attribute ``Manga.ebookjapan_id``
* Attribute ``Manga.myanimelist_id``
* Attribute ``Manga.raw_url``
* Attribute ``Manga.english_translation_url``
* Property ``Manga.anilist_url``
* Property ``Manga.animeplanet_url``
* Property ``Manga.bookwalker_url``
* Property ``Manga.mangaupdates_url``
* Property ``Manga.novelupdates_url``
* Property ``Manga.kitsu_url``
* Property ``Manga.amazon_url``
* Property ``Manga.cdjapan_url``
* Property ``Manga.ebookjapan_url``
* Property ``Manga.myanimelist_url``
* Method ``Manga.__getattr__``
* Method ``Client.logged_in_user()``

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
* :meth:`.ClientUser.manga_chapters`
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
* :meth:`.Manga.follow`
* :meth:`.Manga.unfollow`
* :meth:`.TitleList.parts`
* :meth:`.create_manga`
* :meth:`.create_author`
* :meth:`.Author.update`
* :meth:`.Author.delete`
* :meth:`.Group.update`
* :meth:`.Group.delete`
* :meth:`.create_group`
* :meth:`.CustomList.manga_chapters`
* Two new parameters on :meth:`.logout`: ``delete_tokens`` and ``clear_login_info``
* :class:`.Captcha`
* :class:`.InvalidCaptcha`
* :meth:`.solve_captcha`
* :meth:`.MangadexClient.create`
* :meth:`.MangadexClient.activate_account`
* :meth:`.MangadexClient.resend_activation_code`
* :meth:`.MangadexClient.reset_password_email`
* :meth:`.MangadexClient.finish_password_reset`


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
* Fixed a bug in :meth:`.MangadexClient.request` that prevented the use of non-string and non-iterable objects such as integers and floats.
* Added a client-side fix for the incorrect spelling of the word ``hiatus`` on the MangaDex API.
* Fixed a typo on :attr:`.Demographic.JOSEI` where the term "josei" was actually spelled "josel".
* Added a message to :class:`.Unauthorized`.
* Fixed a bunch of places where requests are not properly closed.
* Changed the value of ``MangaStatus.ABANDONED`` to match new API specifications.
* Fixed a bug in the retry mechanism of :meth:`.MangadexClient.request` that added the parameters for a second time.

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
