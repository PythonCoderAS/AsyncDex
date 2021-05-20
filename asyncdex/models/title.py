from typing import List, Optional, Tuple


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

    def parts(self) -> Tuple[str, List[str]]:
        """Return the parts of this Title List.

        .. versionadded:: 0.5

        :return: The first title and a list of all remaining titles.
        :rtype: Tuple[str, List[str]]
        """
        return self[0], self[1:]
