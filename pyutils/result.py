from __future__ import annotations
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
F = TypeVar("F")


class Result(Generic[T, E]):
    """
    Represents either success — Ok(value) — or failure — Err(error).

    State is tracked via an explicit boolean flag so that Ok(None) and
    Err(None) are both valid and distinguishable states.
    """
    __slots__ = ("_value", "_error", "_is_ok")
    __match_args__ = ("_value", "_error")

    def __init__(self, value: object, error: object, is_ok: bool) -> None:
        self._value = value
        self._error = error
        self._is_ok = is_ok

    # ------------------------------------------------------------------ #
    # constructors

    @staticmethod
    def ok(value: T) -> "Result[T, E]":
        """Wrap a success value."""
        return Result(value, None, True)

    @staticmethod
    def err(error: E) -> "Result[T, E]":
        """Wrap a failure value."""
        return Result(None, error, False)

    # ------------------------------------------------------------------ #
    # checks

    def is_ok(self) -> bool:
        """Return True if this is Ok."""
        return self._is_ok

    def is_err(self) -> bool:
        """Return True if this is Err."""
        return not self._is_ok

    # ------------------------------------------------------------------ #
    # unwrapping

    def unwrap(self) -> T:
        """
        Return the contained Ok value.
        Raises ValueError if this is Err.
        """
        if self.is_err():
            raise ValueError(f"Called unwrap() on an Err Result: {self._error!r}")
        return self._value

    def unwrap_err(self) -> E:
        """
        Return the contained Err value.
        Raises ValueError if this is Ok.
        """
        if self.is_ok():
            raise ValueError(f"Called unwrap_err() on an Ok Result: {self._value!r}")
        return self._error

    def unwrap_or(self, default: T) -> T:
        """Return the Ok value, or *default* if Err."""
        return self._value if self.is_ok() else default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Return the Ok value, or the result of calling *func* with the error."""
        return self._value if self.is_ok() else func(self._error)

    def expect(self, message: str) -> T:
        """
        Return the Ok value, or raise ValueError with *message* if Err.
        Useful for adding context to failures.
        """
        if self.is_err():
            raise ValueError(f"{message}: {self._error!r}")
        return self._value

    # ------------------------------------------------------------------ #
    # dunder methods

    def __repr__(self) -> str:
        return f"Ok({self._value!r})" if self.is_ok() else f"Err({self._error!r})"

    def __bool__(self) -> bool:
        return self.is_ok()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return NotImplemented
        if self.is_ok() and other.is_ok():
            return self._value == other._value
        if self.is_err() and other.is_err():
            return self._error == other._error
        return False

    def __hash__(self) -> int:
        return hash(self._value) if self.is_ok() else hash(self._error)
