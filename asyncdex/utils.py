def remove_prefix(prefix: str, string: str) -> str:
    """Remove a prefix from a string. This is a polyfill for Python versions <3.9.

    :param prefix: The prefix to remove
    :type prefix: str
    :param string: The string to remove the prefix from
    :type string: str
    :return: The string without the prefix
    :rtype: str
    """
    if string[:len(prefix)] == prefix:
        return string[len(prefix):]
    else:
        return string
