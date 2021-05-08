from typing import List, Optional


class TitleList(List[str]):
    """An object representing a list of titles.

    .. versionadded:: 0.2
    """

    @property
    def primary(self) -> Optional[str]:
        """Returns the primary title for the language if it exists or else returns None.

        :return: The first title in the list.
        :rtype: str
        """
        return self[0] if self else None

    def __repr__(self) -> str:
        """Provide a string representation of the object.

        :return: The string representation
        :rtype: str
        """
        return f"{type(self).__name__}{super().__repr__()}"
