"""Package utilities."""


def flatten(nested_list: list) -> list:
    """Flatten nested list of any dimension to single dimension.

    Args:
        Nested_list: list or list of lists of any dimension/depth

    Returns:
        Flattened ``nested_list``.

    >>> a = [1, [2, 3], [[[4, "a"]]]]
    >>> flatten(a)
    [1,2,3,4,"a"]
    """
    if len(nested_list) == 0:
        return nested_list
    if isinstance(nested_list[0], list):
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    return nested_list[:1] + flatten(nested_list[1:])
