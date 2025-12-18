import collections


def patch_collections_for_py3():
    """Add missing ABCs to collections for legacy deps on Python 3.10+."""
    import collections.abc as _abc

    for name in (
        "Container",
        "Iterable",
        "MutableSet",
        "Mapping",
        "MutableMapping",
        "Sequence",
        "Callable",
    ):
        if not hasattr(collections, name):
            setattr(collections, name, getattr(_abc, name))
