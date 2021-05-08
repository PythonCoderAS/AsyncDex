Changelog
#########

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
