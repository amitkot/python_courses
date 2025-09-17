---
title: "Python Metaprogramming & Metaclasses — v4 (demo-rich)"
info: "Single-concept slides with live code demos + presenter notes"
theme: default
lineNumbers: false
fonts:
  sans: Inter
  mono: Fira Code
---

# Python Metaprogramming & Metaclasses

Single‑concept + demo slides

<!--
Use Presenter View (press P). Each concept followed by a demo slide you can run in REPL.
-->

---

## `getattr` — concept

Read attribute by string

<!--
Goal: students see string-based introspection. Tie to dynamic loading/config.
-->

---

## `getattr` — demo

```py
class Box:
    pass
b = Box()
b.x = 10

print(getattr(b, "x"))         # 10
print(getattr(b, "missing", 0))# 0
```

---

## `setattr` / `delattr` — concept

Set/delete attribute by string

<!--
Useful for loading dict configs into objects.
-->

---

## `setattr` / `delattr` — demo

```py
class C:
    pass

c = C()
setattr(c, "mode", "debug")
print(c.mode)     # "debug"
delattr(c, "mode")
```

---

## `vars` / `dir` — concept

Inspect attributes

<!--
vars(obj) ≈ obj.__dict__ (if writable); dir(obj) for discoverability.
-->

---

## `vars` / `dir` — demo

```py
class User:
    pass

u = User()
u.name = "Ada"
print(vars(u))     # {'name': 'Ada'}
print(u.__dict__)  # {'name': 'Ada'}
print("name" in dir(u))
```

---

## `vars` / `dir` — demo

```py
class User:
    pass

u = User()
u.name = "Ada"
dir(u)
# ['__class__',
#  '__delattr__',
#  '__dict__',
#  '__dir__',
#  '__doc__',
#  '__eq__',
#  '__format__',
#  '__ge__',
#  '__getattribute__',
#  '__getstate__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__init_subclass__',
#  '__le__',
#  '__lt__',
#  '__module__',
#  '__ne__',
#  '__new__',
#  '__reduce__',
#  '__reduce_ex__',
#  '__repr__',
#  '__setattr__',
#  '__sizeof__',
#  '__str__',
#  '__subclasshook__',
#  '__weakref__',
#  'name']
```

---

## Attribute lookup — concept

instance → class → bases

<!--
Keep it simple (no descriptors yet). This explains where injected attrs come from.
-->

---

## `type()` (inspect) — concept

The class of an object

---

## `type()` (inspect) — demo

```py
type(42)           # <class 'int'>
type(str)          # <class 'type'>
```

---

## `type(name,bases,ns)` — concept

Create a class dynamically

<!--
We will use this for "Dynamic DTOs from JSON schema".
-->

---

## `type(name,bases,ns)` — demo

```py
def shout(self):
    return self.msg + "!"

Greeter = type("Greeter", (object,), {"msg": "hi", "shout": shout})

g = Greeter()
print(g.shout())  # hi!
```

---

## Dynamic DTOs from JSON schema — concept

Map schema dict ➜ `type(name,bases,ns)`

<!--
Explain: in tests or codegen you may have a schema (fields/types). Build DTO classes on the fly to validate/hold data.
-->

---

## Dynamic DTOs from JSON schema — demo

```py
schema = {"name": str, "age": int}

def make_dto(name, schema):
    ns = {"__annotations__": schema.copy()}     # type annotations
    # Optional: __init__ from annotations
    def __init__(self, **data):
        for k, t in schema.items():
            v = data.get(k)
            if not isinstance(v, t): raise TypeError(f"{k} must be {t.__name__}")
            setattr(self, k, v)
    ns["__init__"] = __init__
    return type(name, (object,), ns)

UserDTO = make_dto("UserDTO", schema)
u = UserDTO(name="Ada", age=36)
```

---

## Resolve metaclass — concept

default: `type`

---

## Metaclass `__new__`

Called when defining a new class, allocates and returns the class object

---

## Metaclass `__new__`

```python
class MyMeta(type):
    def __new__(mcls, name, bases, ns):
        print("--- Starting MyMeta __new__()")
        print(f"__new__: cls is {mcls}")
        print(f"__new__: name is {name}")
        print(f"__new__: bases is {bases}")
        print(f"__new__: ns is {ns}")
        return super().__new__(mcls, name, bases, ns)

class MyBase: pass

class MyClass(MyBase, metaclass=MyMeta):
    def __init__(self, a, b): pass
```

```python
--- Starting MyMeta __new__()
__new__: mcls is <class '__main__.MyMeta'>
__new__: name is MyClass
__new__: bases is (<class '__main__.MyBase'>,)
__new__: ns is {'__module__': '__main__', '__qualname__': 'MyClass', '__init__': <function MyClass.__init__ at 0x1074470e0>}
```

---

## Metaclass `__init__`

Called when defining a new class, receives an allocated class and sets up its attributes (functions, class variables)

---

## Metaclass `__init__`

```python
class MyMeta(type):
    def __init__(mcls, name, bases, ns):
        print("--- Starting MyMeta __init__()")
        print(f"__init__: mcls is {mcls}")
        print(f"__init__: name is {name}")
        print(f"__init__: bases is {bases}")
        print(f"__init__: ns is {ns}")
        super().__init__(name, bases, ns)

class MyBase: pass

class MyClass(MyBase, metaclass=MyMeta):
    def __init__(self, a, b): pass
```

```python
--- Starting MyMeta __init__()
__init__: mcls is <class '__main__.MyClass'>
__init__: name is MyClass
__init__: bases is (<class '__main__.MyBase'>,)
__init__: ns is {'__module__': '__main__', '__qualname__': 'MyClass', '__init__': <function MyClass.__init__ at 0x1074470e0>}
```

---
hide: true
---

## Execute body — concept

Python fills mapping by executing the class body

---
hide: true
---

## `__new__` — concept

Transform namespace ➜ create class

---
hide: true
---

## `__new__` — demo (inject repr/init/slots)

```py
class AutoStruct(type):
    def __new__(mcls, name, bases, ns, **kw):
        ann = ns.get("__annotations__", {})
        fields = list(ann)
        # inject slots
        ns.setdefault("__slots__", tuple(fields))
        # remove defaults from class dict to avoid slot shadowing
        defaults = {k: ns.pop(k) for k in list(ns.keys()) if k in fields}
        # inject __init__
        def __init__(self, *args, **kwargs):
            vals = dict(zip(fields, args)); vals.update(kwargs)
            for f in fields:
                val = vals.get(f, defaults.get(f))
                setattr(self, f, val)
        ns["__init__"] = __init__
        # inject __repr__
        def __repr__(self):
            return f"{name}(" + ", ".join(f"{f}={getattr(self,f)!r}" for f in fields) + ")"
        ns["__repr__"] = __repr__
        return super().__new__(mcls, name, bases, ns)

class Point(metaclass=AutoStruct):
    __annotations__ = {"x": int, "y": int}
    x: int; y: int

p = Point(2, 3); repr(p)
```

---

## `__init__` (metaclass) — concept

- Finalize class object
- Good for light registration or consistency checks. Keep heavy transforms in __new__.

---

## Class creation protocol — concept

class body ➜ `__prepare__` ➜ `__new__` ➜ `__init__`

---

## `__prepare__` — concept

- If present, `__prepare__` is called when defining a new class.
- Should be on the metaclass as a `@classmethod`.
- Used to customize the class namespace dict.

---

## `__prepare__` — demo

```py
class CollectFields(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        """Will be used in __new__"""
        class NS(dict):
            def __setitem__(self, k, v):
                if k.islower():  # forbid lowercase constants
                    pass
                super().__setitem__(k, v)
        return NS()

    def __new__(mcls, name, bases, ns, **kw):
        ns["FIELDS"] = [k for k in ns.keys() if k.isupper()]
        return super().__new__(mcls, name, bases, dict(ns))

class Model(metaclass=CollectFields):
    ID = 0
    NAME = "N/A"
# Model.FIELDS == ["ID", "NAME"]
```

**Where does `__prepare__` live?** On the **metaclass**.
**What is it good for?** Enforcing rules during class body execution, collecting names, validating duplicates.

<!--
Next slides split steps.
-->

---

## Instance lifecycle — concept

`__new__` (allocate) vs `__init__` (initialize)

---

## Decorator vs Metaclass — concept

When to choose which?

---

## Decorator vs Metaclass — demo (comparison)

```py
# Decorator adds a .debug() method post-creation
def add_debug(cls):
    def debug(self):
        return vars(self)
    cls.debug = debug
    return cls

@add_debug
class A: pass
```

```py
# Metaclass enforces a class-level invariant at creation
class Named(type):
    def __new__(mcls, name, bases, ns, **kw):
        if "NAME" not in ns:
            raise TypeError("Must define NAME")
        return super().__new__(mcls, name, bases, ns)

class B(metaclass=Named):
    NAME = "service"
```

---

## `__init_subclass__` — concept

Hook that runs on subclass creation

<!--
Allows base classes to react to new subclasses without a metaclass.
-->

---

## `__init_subclass__` — demo (registry & validation)

```py
class Command:
    registry = {}
    def __init_subclass__(cls, *, name=None, **kw):
        super().__init_subclass__(**kw)
        if name is None:
            raise TypeError("Provide a command name")
        if name in Command.registry:
            raise ValueError("Duplicate command name")
        Command.registry[name] = cls

class List(Command, name="list"): pass
class Add(Command, name="add"): pass

# Command.registry -> {"list": List, "add": Add}
```

---
hide: true
---

## CLI Image Plugins — concept

Registry resolves command ➜ class ➜ `apply(image, **opts)`

---
hide: true
---

## CLI Image Plugins — demo (decorator + metaclass)

```py
# Using decorator (Lab 1)
# registry = {"resize": Resize, "crop": Crop, "emoji": Emoji}

def run(command, image, **opts):
    cls = registry[command]
    return cls().apply(image, **opts)

print(run("resize", "img.jpg", width=100, height=80))

# Using metaclass auto-registration
# class BasePlugin(metaclass=PluginMeta): __abstract__ = True
# subclasses register themselves in PluginMeta.__init__
```

---

## `metaclass.__call__` — concept

Control instance creation

---

## `metaclass.__call__` — demo (singleton)

```py
class SingletonMeta(type):
    def __call__(cls, *a, **k):
        if not hasattr(cls, "_inst"):
            cls._inst = super().__call__(*a, **k)
        return cls._inst

class Settings(metaclass=SingletonMeta):
    def __init__(self, env="prod"): self.env = env

s1 = Settings(); s2 = Settings()
assert s1 is s2
```

---
hide: true
---

## Debugging — concept

`inspect.getsource()` and `dis.dis()`

---
hide: true
---

## Debugging — demo

```py
import inspect, dis

def foo(x): return x + 1
print(inspect.getsource(foo))   # prints source

# disassemble a small function
def bar(a,b): return a*b + 2
dis.dis(bar)
```

---

## Summary

- Small tools first (decorator/`__init_subclass__`), metaclasses when you need creation/instantiation control.
- Patterns: registry, strict struct, singleton/multiton.
