from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


# ========== Q1 solution: Properties ==========
class PersonV1:
    def __init__(self, name: str, age: int, email: str) -> None:
        self._name = ""
        self._age = 0
        self._email = ""
        self.name = name
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise TypeError("name must be a non-empty str")
        self._name = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise TypeError("age must be int >= 0")
        self._age = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str) or "@" not in value:
            raise TypeError("email must contain '@'")
        self._email = value.strip().lower()


# ========== Q2 solution: Descriptor ==========
class Field(Generic[T]):
    def __init__(
        self,
        *,
        validator: Callable[[T], T] | None = None,
        coerce: Callable[[Any], T] | None = None,
    ) -> None:
        self.validator = validator
        self.coerce = coerce
        self.name = "<unbound>"

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> T:
        if instance is None:
            return self  # type: ignore[return-value]
        return instance.__dict__[self.name]  # type: ignore[return-value]

    def __set__(self, instance: Any, value: Any) -> None:
        if self.coerce is not None:
            value = self.coerce(value)
        if self.validator is not None:
            value = self.validator(value)
        instance.__dict__[self.name] = value


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


class Person:
    name: str = Field(validator=ensure_str_non_empty)
    age: int = Field(validator=ensure_int_ge0)
    email: str = Field(coerce=normalize_email, validator=ensure_email)

    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name
        self.age = age
        self.email = email


if __name__ == "__main__":
    pv1 = PersonV1("Amit", 44, "  AMIT@EXAMPLE.COM ")
    assert pv1.name == "Amit"
    assert pv1.age == 44
    assert pv1.email == "amit@example.com"

    p = Person("Amit", 44, "  AMIT@EXAMPLE.COM ")
    assert p.name == "Amit"
    assert p.age == 44
    assert p.email == "amit@example.com"

    print("Mini-lab: all checks passed.")