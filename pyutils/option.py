from __future__ import annotations
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")

_MISSING = object()  # sentinel which allows Some(None) to be valid

class Option(Generic[T]):
    """
    Represents an optional value: either Some(value) or None.
    Some(None) is a valid and distinct state from none().
    """

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: object) -> None:
        self._value = value

    # ------------------------------------------------------------------ #
    # constructors 

    @staticmethod
    def some(value: T) -> "Option[T]":
        """Wrap a value in Some."""
        return Option(value)

    @staticmethod
    def none() -> "Option[T]":
        """Return the None variant."""
        return Option(_MISSING)

    # ------------------------------------------------------------------ #
    # checks

    def is_some(self) -> bool:
        """Return True if this is a Some value."""
        return self._value is not _MISSING

    def is_none(self) -> bool:
        """Return True if this is None."""
        return self._value is _MISSING

    # ------------------------------------------------------------------ #
    # unwrapping

    def unwrap(self) -> T:
        """
        Return the contained value.
        Raises ValueError if this is None.
        """
        if self.is_none():
            raise ValueError("Called unwrap() on a None Option")
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Return the contained value, or *default* if None."""
        return self._value if self.is_some() else default

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Return the contained value, or the result of calling *func* if None."""
        return self._value if self.is_some() else func()
    
    # ------------------------------------------------------------------ #
    # dunder methods

    def __repr__(self) -> str:
        return f"Some({self._value!r})" if self.is_some() else "None"

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Option):
            return NotImplemented
        if self.is_none() and other.is_none():
            return True
        if self.is_some() and other.is_some():
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value) if self.is_some() else hash(_MISSING)

    def __iter__(self):
        """Allows: value, = option  (unpacking a Some of one element)."""
        if self.is_some():
            yield self._value
