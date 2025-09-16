from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


# ========== Q2: Descriptor ==========
class Field(Generic[T]):
    """Minimal reusable **data descriptor**.

    - __set_name__: learn attribute name
    - __get__: return self if instance is None; else instance.__dict__[name]
    - __set__: optional coerce -> validator -> store in instance.__dict__
    """

    def __init__(
        self,
        *,
        validator: Callable[[T], T] | None = None,
        coerce: Callable[[Any], T] | None = None,
    ) -> None:
        # TODO: store callables; you'll also need to remember the attribute name
        raise NotImplementedError

    def __set_name__(self, owner: type, name: str) -> None:
        # TODO
        raise NotImplementedError

    def __get__(self, instance: Any, owner: type | None = None) -> T:
        # TODO
        raise NotImplementedError

    def __set__(self, instance: Any, value: Any) -> None:
        # TODO
        raise NotImplementedError


# Helpers you can reuse in properties and descriptor


def ensure_str_non_empty(v: Any) -> str:
    if not isinstance(v, str) or not v.strip():
        raise TypeError("must be a non-empty str")
    return v


def ensure_int_ge0(v: Any) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise TypeError("must be int >= 0")
    return v


def normalize_email(v: Any) -> str:
    if not isinstance(v, str):
        raise TypeError("email must be str")
    return v.strip().lower()


def ensure_email(v: str) -> str:
    if "@" not in v:
        raise TypeError("email must contain '@'")
    return v


# Target class using the descriptor
class Person:
    # TODO: replace with Field(...) instances using the helpers above
    # name  = Field(validator=ensure_str_non_empty)
    # age   = Field(validator=ensure_int_ge0)
    # email = Field(coerce=normalize_email, validator=ensure_email)
    def __init__(self, name: str, age: int, email: str) -> None:
        # TODO: assign via descriptors
        raise NotImplementedError


if __name__ == "__main__":
    print("Mini-Lab: run tests after you implement Q1/Q2.\n")

    # --- Q2 checks (uncomment after you implement Field/Person) ---
    # p = Person("Amit", 44, "  AMIT@EXAMPLE.COM ")
    # assert p.name == "Amit"
    # assert p.age == 44
    # assert p.email == "amit@example.com"
    # print("Q2 OK")
