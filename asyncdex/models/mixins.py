from datetime import datetime
from typing import Dict, Optional, TypeVar

from ..utils import copy_key_to_attribute

_T = TypeVar("_T", bound="DatetimeMixin")


class DatetimeMixin:
    """A mixin for models with ``created_at`` and ``updated_at`` attributes.

    .. versionadded:: 0.2
    """

    created_at: datetime
    """A :class:`datetime.datetime` representing the object's creation time.

    .. seealso:: :meth:`.modified_at`

    .. note::
        The datetime is **timezone aware** as it is parsed from an ISO-8601 string.
    """

    updated_at: Optional[datetime]
    """A :class:`datetime.datetime` representing the last time the object was updated. May be None if the object was 
    never updated after creation.

    .. seealso:: :meth:`.modified_at`

    .. note::
        The datetime is **timezone aware** as it is parsed from an ISO-8601 string.
    """

    @property
    def modified_at(self) -> datetime:
        """The last time the object was modified. This will return the creation time if the object was never updated
        after creation, or the modification time if it has.

        .. seealso:: :attr:`.created_at`, :attr:`.updated_at`

        :return: The last time the object was changed as a :class:`datetime.datetime` object.

            .. note::
                The datetime is **timezone aware** as it is parsed from an ISO-8601 string.

        :rtype: :class:`datetime.datetime`
        """
        return self.updated_at or self.created_at

    def _process_times(self, attributes: Dict[str, str]):
        copy_key_to_attribute(
            attributes,
            "createdAt",
            self,
            "created_at",
            transformation=lambda attrib: datetime.fromisoformat(attrib) if attrib else attrib,
        )
        copy_key_to_attribute(
            attributes,
            "updatedAt",
            self,
            "updated_at",
            transformation=lambda attrib: datetime.fromisoformat(attrib) if attrib else attrib,
        )

    def __lt__(self: _T, other: _T) -> bool:
        """Compares the two object's creation times to find if the current model's creation time is less than the
        other model's creation time.

        .. versionadded:: 0.3

        :param other: The other model.
        :type other: DatetimeMixin
        :return: Whether or not the current model's creation time is less than the other model's creation time.
        :rtype: bool
        """
        if type(self) == type(other):
            return self.created_at < other.created_at
        return NotImplemented

    def __le__(self: _T, other: _T) -> bool:
        """Compares the two object's creation times to find if the current model's creation time is less than or
        equal to the other model's creation time.

        .. versionadded:: 0.3

        :param other: The other model.
        :type other: DatetimeMixin
        :return: Whether or not the current model's creation time is less than or equal to the other model's creation
            time.
        :rtype: bool
        """
        if type(self) == type(other):
            return self.created_at <= other.created_at
        return NotImplemented

    def __gt__(self: _T, other: _T) -> bool:
        """Compares the two object's creation times to find if the current model's creation time is greater than the
        other model's creation time.

        .. versionadded:: 0.3

        :param other: The other model.
        :type other: DatetimeMixin
        :return: Whether or not the current model's creation time is greater than the other model's creation time.
        :rtype: bool
        """
        if type(self) == type(other):
            return self.created_at > other.created_at
        return NotImplemented

    def __ge__(self: _T, other: _T) -> bool:
        """Compares the two object's creation times to find if the current model's creation time is greater than or
        equal to the other model's creation time.

        .. versionadded:: 0.3

        :param other: The other model.
        :type other: DatetimeMixin
        :return: Whether or not the current model's creation time is greater than or equal to the other model's creation
            time.
        :rtype: bool
        """
        if type(self) == type(other):
            return self.created_at >= other.created_at
        return NotImplemented
