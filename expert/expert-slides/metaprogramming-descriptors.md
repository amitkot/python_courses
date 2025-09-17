---
layout: cover
title: Python Descriptors
subtitle: Metaprogramming — controlling attribute access
class: text-center
---

# Python Descriptors

## Metaprogramming — controlling attribute access

<div class="text-xl font-semibold">Amit Kotlovski</div>
<div class="text-base"><a href="mailto:amit@amitkot.com">amit@amitkot.com</a></div>

---

# Why Descriptors?

- Hook into attribute access (`obj.attr`)
- Foundation for `@property`, methods, classmethod/staticmethod
- Power reusable attribute behavior (validation, caching, ORM fields)

---

# Big Picture

- **Descriptor**: any object with `__get__`, `__set__`, or `__delete__`
- Lives on the **class**, not the instance
- Python calls it during attribute lookup

---

# `property` is a Descriptor

```python
class Example:
    def __init__(self) -> None:
        self._x: int = 0

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        if value < 0:
            raise ValueError("x >= 0")
        self._x = value
```

- `property` implements `__get__`/`__set__`/`__delete__`

---

# Descriptor Protocol (skeleton)

```python
from typing import Any

class Descriptor:
    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        ...
    def __set__(self, instance: Any, value: Any) -> None:
        ...
    def __delete__(self, instance: Any) -> None:
        ...
```

- Implement any subset; Python adapts

---

# Data vs Non‑Data

- **Data**: has `__set__` or `__delete__` → takes precedence over instance `__dict__`
- **Non‑Data**: only `__get__` → overridden by instance `__dict__`

```python
from typing import Any

class NonData:
    def __get__(self, inst: Any, owner: type | None = None) -> str:
        return "from descriptor"

class C:
    x = NonData()

c = C()
c.__dict__["x"] = "from dict"
assert c.x == "from dict"  # non‑data yields
```

---

# `__set_name__`: learn your attribute name

```python
from typing import Any

class Named:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name  # set at class creation

    def __get__(self, inst: Any, owner: type | None = None) -> Any:
        return f"accessing {self.name}"

class C:
    field = Named()
```

```python
c = C()
print(c.field)          # "accessing field"
```

- Useful to avoid passing the attribute name manually

---

# Reusable Validator (Positive)

```python
from typing import Any

class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, inst: Any, owner: type | None = None) -> Any:
        if inst is None:
            return self
        return inst.__dict__[self.name]

    def __set__(self, inst: Any, value: float) -> None:
        if value < 0:
            raise ValueError(f"{self.name} must be >= 0")
        inst.__dict__[self.name] = value

class Account:
    balance = Positive()
    def __init__(self, balance: float) -> None:
        self.balance = balance
```

---

# Typed Field (runtime type enforcement)

```python
from typing import Any, Type

class Typed:
    def __init__(self, typ: Type[Any]) -> None:
        self.typ = typ

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, inst: Any, owner: type | None = None) -> Any:
        if inst is None:
            return self
        return inst.__dict__[self.name]

    def __set__(self, inst: Any, value: Any) -> None:
        if not isinstance(value, self.typ):
            raise TypeError(f"{self.name} must be {self.typ.__name__}")
        inst.__dict__[self.name] = value

class User:
    id = Typed(int)
    name = Typed(str)
```

---

# Lazy Property (compute once, cache)

```python
from typing import Any, Callable

class lazyprop:
    def __init__(self, fget: Callable[[Any], Any]) -> None:
        self.fget = fget
        self.name = fget.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, inst: Any, owner: type | None = None) -> Any:
        if inst is None:
            return self
        if self.name not in inst.__dict__:
            inst.__dict__[self.name] = self.fget(inst)
        return inst.__dict__[self.name]
```

---

# Lazy Property (reset via delete)

```python
from typing import Any

class lazyprop_reset(lazyprop):
    def __delete__(self, inst: Any) -> None:
        inst.__dict__.pop(self.name, None)
```

- `del obj.attr` clears cache → next access recomputes

---

# Mini‑ORM Field (proxy to storage)

```python
from typing import Any, Callable

class Field:
    def __init__(self, loader: Callable[[Any, str], Any],
                 saver: Callable[[Any, str, Any], None]) -> None:
        self.loader, self.saver = loader, saver

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, inst: Any, owner: type | None = None) -> Any:
        if inst is None:
            return self
        return self.loader(inst, self.name)

    def __set__(self, inst: Any, value: Any) -> None:
        self.saver(inst, self.name, value)

class Row:
    _store: dict[str, Any]
    name = Field(lambda r, k: r._store.get(k),
                 lambda r, k, v: r._store.__setitem__(k, v))
    def __init__(self) -> None:
        self._store = {}
```

---

# Methods are Descriptors

```python
from types import MethodType

class C:
    def f(self) -> str:
        return "hi"

c = C()
# What Python does under the hood:
bound = C.__dict__["f"].__get__(c, C)  # -> MethodType
assert isinstance(bound, MethodType)
assert bound() == "hi"
```

- `function.__get__` binds `self`

---

# Lookup Order (simplified)

1. **Data descriptor** on class → use it
2. Instance `__dict__`
3. Attribute on class (incl. **non‑data descriptor**) → if descriptor, call `__get__`
4. `__getattr__` fallback

- Explains why data descriptors beat instance values

---

# `__getattr__` vs `__getattribute__`

- `__getattribute__`: intercept **every** attribute access
- `__getattr__`: called **only if** normal lookup fails
- Descriptors participate **before** `__getattr__`

```python
class Spy:
    def __getattribute__(self, name: str):
        print("getattribute", name)
        return super().__getattribute__(name)
```

---

# Common Pitfalls

- Storing per‑instance data **on the descriptor** (shared!)
- Infinite recursion: don’t access via `self.name` property inside `__get__`
- Fix: always use `inst.__dict__[self.name]`

```python
# BAD: self.storage[inst] ... (unless using WeakKeyDictionary)
# GOOD: inst.__dict__[self.name] = value
```

---

# When to Use What

- **`@property`**: one attribute, local logic
- **Descriptor class**: reusable logic across many attributes; libraries/frameworks
- **`dataclasses` / `pydantic`**: higher‑level modeling, validation

---

# Testing & Debugging

- Assert precedence with instance `__dict__`
- Inspect class dict: `C.__dict__['field']`
- Check descriptor category (data vs non‑data)

```python
def is_data_descriptor(obj: object) -> bool:
    return any(hasattr(obj, m) for m in ("__set__", "__delete__"))
```

---

# Lab

- Convert 3 `@property` validators into one `Descriptor` class
- Add `__set_name__`
- Extend to support default values & docstrings

---

# Takeaways

- Descriptors = precise control of attribute semantics
- They power many Python features you already use
- Great tool for reusable, framework‑level behaviors

---

# Questions

---
layout: center
class: text-center
---

# Thanks!

- <div class="text-xl font-semibold">Amit Kotlovski</div>
- <div class="text-base"><a href="mailto:amit@amitkot.com">amit@amitkot.com</a></div>
