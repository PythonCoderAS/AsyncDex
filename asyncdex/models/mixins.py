from datetime import datetime
from typing import Dict, Optional

from ..utils import copy_key_to_attribute


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

        .. seealso:: :attr:`.created_at`
        .. seealso:: :attr:`.updated_at`

        :return: The last time the object was changed as a :class:`datetime.datetime` object.

            .. note::
                The datetime is **timezone aware** as it is parsed from an ISO-8601 string.

        :rtype: :class:`datetime.datetime`
        """
        return self.updated_at or self.created_at

    def _process_times(self, attributes: Dict[str, str]):
        copy_key_to_attribute(attributes, "createdAt", self, "created_at",
                              transformation=lambda attrib: datetime.fromisoformat(attrib) if attrib else attrib)
        copy_key_to_attribute(attributes, "updatedAt", self, "updated_at",
                              transformation=lambda attrib: datetime.fromisoformat(attrib) if attrib else attrib)
