from enum import Enum


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
    JOSEI = "josel"
    """A Josei Manga."""
    SEINEN = "seinen"
    """A Seinen Manga."""


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
    ABANDONED = "abandoned"
    """A manga where the author has intentionally stopped publishing new chapters."""


class FollowStatus(Enum):
    """An Enum representing the status that the user has marked the manga has. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Manga-reading-status

    .. versionadded:: 0.2
    """
    READING = 'reading'
    """A manga that the user has marked as reading."""
    ON_HOLD = 'on_hold'
    """A manga that the user has marked as on_hold."""
    PLAN_TO_READ = 'plan_to_read'
    """A manga that the user has marked as plan_to_read."""
    DROPPED = 'dropped'
    """A manga that the user has marked as dropped."""
    RE_READING = 're_reading'
    """A manga that the user has marked as re_reading."""
    COMPLETED = 'completed'
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
    SAFE = 'safe'
    """A manga that is safe.
    
    .. note::
        This is the only content rating that means a manga is safe for work. All other values are not safe for work
        (NSFW).
    """
    SUGGESTIVE = 'suggestive'
    """A manga that is suggestive.
    
    .. note::
        This type of content represents content tagged with the ``Ecchi`` tag.
    """
    EROTICA = 'erotica'
    """A manga that is erotica.
    
    .. note::
        This type of content represents content tagged with the ``Smut`` tag.
    """
    PORNOGRAPHIC = 'pornographic'
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
    PUBLIC = 'public'
    """A public :class:`.CustomList`."""
    PRIVATE = 'private'
    """A private :class:`.CustomList`."""


class Relationship(Enum):
    """An enum representing the different types of relationship types. Source:
    https://api.mangadex.org/docs.html#section/Static-data/Relationship-types

    .. versionadded:: 0.2
    """
    MANGA = 'manga'
    """A :class:`.Manga` resource."""
    CHAPTER = 'chapter'
    """A :class:`.Chapter` resource."""
    AUTHOR = 'author'
    """A :class:`.Author` resource."""
    ARTIST = 'artist'
    """A :class:`.Author` resource."""
    SCANLATION_GROUP = 'scanlation_group'
    """A :class:`.Group` resource."""
    TAG = 'tag'
    """A :class:`.Tag` resource."""
    USER = 'user'
    """A :class:`.User` resource."""
    CUSTOM_LIST = 'custom_list'
    """A :class:`.CustomList` resource."""
