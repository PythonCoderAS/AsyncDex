Changelog
#########

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
