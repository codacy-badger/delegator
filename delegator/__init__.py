__version__ = '0.1.0'

"""
    delegator
    ~~~~~~~~~

    Similar to `def_delegator` in Ruby, allows to forward/delegate attributes
    and methods to some attribute on the object. Supports setting and deleting.

    User-interface consists of:

        - `delegate` class decorator
        - `delegator` class decorator
        - `Delegator` metaclass

    All methods are interchangeable. `delegate` requires passing arguments
    directly, wheares `delegator` and `Delegator` read configuration from
    `delegate` attribute on the target class. For examples see `tests.py`.
"""
from typing import Any, Union, Type, Sequence


class Delegated(object):
    """
    Your typical, run-of-the-mill attribute accessor.
    Forwards access to attribute <attr_name> from owner to <del_name>
    attribute on the owner.
    """
    def __init__(self, name: str, attr: str) -> None:
        self.attr_name = attr
        self.del_name = name

    def __get__(self, instance: str, owner: object) -> Any:
        if instance is None:
            return self
        else:
            return getattr(self.delegate(instance), self.attr_name)

    def __set__(self, instance: str, value: Any) -> None:
        setattr(self.delegate(instance), self.attr_name, value)

    def __delete__(self, instance: str) -> None:
        delattr(self.delegate(instance), self.attr_name)

    def delegate(self, instance: str) -> Any:
        return getattr(instance, self.del_name)


def decorate(cls, src: str = None, attrs: Sequence[str] = None) -> Type:
    """
    This is where the class is actually modified.
    """
    if not (src and attrs) and hasattr(cls, 'delegate'):
        if isinstance(cls.delegate, tuple):
            src, attrs = cls.delegate[0], cls.delegate[1:]

        elif isinstance(cls.delegate, str):
            delegate = cls.delegate.split(' ')
            src, attrs = delegate[0], delegate[1:]

    if src and attrs:
        for attr in attrs:
            setattr(cls, attr, Delegated(src, attr))
    else:
        raise ValueError(
            "Invalid arguments to 'decorate': %s, %s" % (src, attrs)
        )

    return cls


def delegator(cls: Type) -> Type:
    return decorate(cls)


class delegate(object):
    def __init__(self, src: str, *attrs: str) -> None:
        self.src: str
        self.attrs: Sequence[str]

        if src and attrs:
            self.src = src
            self.attrs = attrs
        elif src and isinstance(src, str):
            delegate = src.split(' ')
            self.src, self.attrs = delegate[0], delegate[1:]
        else:
            raise ValueError(
                "Invalid arguments to 'delegate': %s, %s" % (src, attrs)
            )

    def __call__(self, cls: Type) -> Type:
        return decorate(cls, self.src, self.attrs)


class Delegator(type):
    def __new__(*args: Sequence, **kwargs: Sequence):
        return decorate(type.__new__(*args, **kwargs))
