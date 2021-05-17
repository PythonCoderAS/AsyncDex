from enum import Enum, auto


class Demographic(Enum):
    """An Enum representing the various demographics. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Manga-publication-demographic.

    .. versionadded:: 0.2
    """

    SHOUNEN = SHONEN = "shounen"  # Documentation bug on the API's end.
    """A Shounen Manga.
    
    .. note::
        In the developer documentation as of May 7, 2021, there is a typo in the word ``Shounen``, where it is 
        spelled without the ``u``. However, the actual API will only recognize the variant including a ``u``. 
        For the library, both variations can be used for the enum.
    """

    SHOUJO = "shoujo"
    """A Shoujo Manga."""

    JOSEI = "josei"
    """A Josei Manga.
    
    .. versionchanged:: 0.3
        The typo for this field has been corrected.
    """

    SEINEN = "seinen"
    """A Seinen Manga."""

    NONE = "none"
    """A manga without a demographic.
    
    .. versionadded:: 0.4
    """


class MangaStatus(Enum):
    """An Enum representing the various statuses a manga can have. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Manga-status

    .. versionadded:: 0.2

    .. note:: The status of the manga does not dictate whether or not the chapter list will be stable.  Scanlation teams
        may have not published all chapters up to the completion of updates, so the manga may still get new chapters,
        especially in different languages. The only way to know if a manga has actually finished updating is by
        checking if the "end chapter" is present in the current language. Even this is not a guarantee, as an author
        may add additional media accompanying the work, such as a extra page related to the manga on Twitter or
        Pixiv, especially for manga that are mainly published online. The labels shown for a manga's status should
        not dictate the policy for update checking, as they are only meant to be an aid for end users and not actually
        representative of the immutability of the manga's chapter list.
    """

    ONGOING = "ongoing"
    """A manga that is actively being published, in volume format, in a magazine like Weekly Shonen, or online."""

    COMPLETED = "completed"
    """A manga that has finished publication."""

    HIATUS = "hiatus"
    """A manga where the author is on a known hiatus."""

    CANCELLED = ABANDONED = "cancelled"
    """A manga where the author has intentionally stopped publishing new chapters.
    
    .. versionchanged:: 0.3
        The MangaDex API changed the value from ``abandoned`` to ``cancelled``. ``MangaStatus.ABANDONED`` will 
        continue to represent the right value, but calling the enum with ``abandoned`` will not.
    """


class FollowStatus(Enum):
    """An Enum representing the status that the user has marked the manga has. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Manga-reading-status

    .. versionadded:: 0.2
    """

    READING = "reading"
    """A manga that the user has marked as reading."""

    ON_HOLD = "on_hold"
    """A manga that the user has marked as "on hold"."""

    PLAN_TO_READ = "plan_to_read"

    """A manga that the user has marked as "plan to read"."""
    DROPPED = "dropped"
    """A manga that the user has marked as dropped."""

    RE_READING = "re_reading"
    """A manga that the user has marked as rereading."""

    COMPLETED = "completed"
    """A manga that the user has marked as completed.
    
    .. warning::
        When a manga is marked as completed, the MangaDex API drops all chapter read markers. Setting a manga as 
        completed **will** result in the deletion of data. Be very careful!
    """


class ContentRating(Enum):
    """An Enum representing the content in a manga. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Manga-content-rating

    .. versionadded:: 0.2
    """

    SAFE = "safe"
    """A manga that is safe.
    
    .. note::
        This is the only content rating that means a manga is safe for work. All other values are not safe for work
        (NSFW).
    """

    SUGGESTIVE = "suggestive"
    """A manga that is suggestive.
    
    .. note::
        This type of content represents content tagged with the ``Ecchi`` tag.
    """

    EROTICA = "erotica"
    """A manga that is erotica.
    
    .. note::
        This type of content represents content tagged with the ``Smut`` tag.
    """

    PORNOGRAPHIC = "pornographic"
    """A manga that is pornographic.
    
    .. note::
        This type of content was the only type of content that MangaDex's old 18+ filter used to block. This type of 
        content was also the type of content that old MangaDex APIs used to call "hentai".
    """


class Visibility(Enum):
    """An enum representing the visibility of an :class:`.CustomList`. Source:
    https://api.mangadex.org/docs.html#section/Static-data/CustomList-visibility

    .. versionadded:: 0.2
    """

    PUBLIC = "public"
    """A public :class:`.CustomList`."""

    PRIVATE = "private"
    """A private :class:`.CustomList`."""


class Relationship(Enum):
    """An enum representing the different types of relationship types. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Relationship-types

    .. versionadded:: 0.2
    """

    MANGA = "manga"
    """A :class:`.Manga` resource."""

    CHAPTER = "chapter"
    """A :class:`.Chapter` resource."""

    AUTHOR = "author"
    """A :class:`.Author` resource."""

    ARTIST = "artist"
    """A :class:`.Author` resource."""

    SCANLATION_GROUP = "scanlation_group"
    """A :class:`.Group` resource."""

    TAG = "tag"
    """A :class:`.Tag` resource."""

    USER = "user"
    """A :class:`.User` resource."""

    CUSTOM_LIST = "custom_list"
    """A :class:`.CustomList` resource."""


class DuplicateResolutionAlgorithm(Enum):
    """An enum representing the various methods of resolving duplicate chapters in the same language.

    .. versionadded:: 0.3

    .. note::
        The filtering algorithms are short-circuiting, meaning that once the chapters for a certain chapter number is
        lowered down to one item, it will be returned.

    Operation order:

    #. Previous group
    #. Specific Group
    #. Specific User
    #. Creation Date ascending/descending/Views ascending/descending

    .. note::
        It is an error to specify more than one of the lowest-priority operations, since they all return only one
        value. Doing so will raise an error.
    """

    PREVIOUS_GROUP = auto()
    """A resolution strategy that attempts to use the same group for the chapter as the previous chapter. This needs 
    an accompanying strategy to determine the initial group.
    
    .. seealso:: :attr:`.SPECIFIC_GROUP`
    """

    SPECIFIC_GROUP = auto()
    """A resolution strategy that attempts to only select certain groups. This needs an accompanying strategy for 
    chapters where the group is not present.
    
    .. seealso:: :attr:`.SPECIFIC_USER`
    """

    SPECIFIC_USER = auto()
    """A resolution strategy that attempts to only select chapters by certain users. This needs an accompanying 
    strategy for chapters where the user ia not present.
    
    .. seealso:: :attr:`.SPECIFIC_GROUP`
    """

    CREATION_DATE_ASC = auto()
    """A resolution strategy that will select the chapter that was created first.
    
    .. seealso:: :attr:`.CREATION_DATE_DESC`
    """

    CREATION_DATE_DESC = auto()
    """A resolution strategy that will select the chapter that was created last.
    
    .. seealso:: :attr:`.CREATION_DATE_ASC`
    """

    VIEWS_ASC = auto()
    """A resolution strategy that will select the chapter with the least views.
    
    .. warning::
        This is not implemented yet as the API does not return view counts.
        
    .. seealso:: :attr:`.VIEWS_DESC`
    """

    VIEWS_DESC = auto()
    """A resolution strategy that will select the chapter with the most views.
    
    .. warning::
        This is not implemented yet as the API does not return view counts.
        
    .. seealso:: :attr:`.VIEWS_ASC`
    """


class OrderDirection(Enum):
    """An enum representing the various directions that can be used for ordering a list of items.

    .. versionadded:: 0.4
    """

    ASCENDING = "asc"
    """Order items from smallest to largest."""

    DESCENDING = "desc"
    """Order items from largest to smallest."""


class TagMode(Enum):
    """An enum representing the various ways tag inclusion/exclusion can be read by the server.

    .. versionadded:: 0.4
    """

    AND = "AND"
    """Manga is included/excluded only if **all** tags are present."""

    OR = "OR"
    """Manga is included/excluded if **any** tag is present."""
