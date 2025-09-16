---
title: "Python Metaprogramming & Metaclasses — Step‑by‑Step"
info: "Advanced Python In Depth · ~3 hours · expanded slide deck"
theme: default
highlighter: shiki
lineNumbers: true
drawings:
  persist: false
fonts:
  sans: Inter
  mono: Fira Code
---

# Python Metaprogramming & Metaclasses

Step‑by‑step edition · ~3 hours

<div class="text-sm opacity-80 mt-2">
We will build concepts incrementally: attribute access → dynamic class creation → class decorators → metaclasses.
</div>

---

## Roadmap

1. **Python's object + attribute model** (the bedrock)
2. **Dynamic class creation** with `type(name, bases, namespace)`
3. **Instance lifecycle**: `__new__` vs `__init__`
4. **Class decorators** and `__init_subclass__`
5. **Metaclasses**: `__prepare__`, `__new__`, `__init__`, `__call__`
6. **Patterns & labs**: registry, strict struct, multiton cache

---

## 0. Pre-flight: the attribute model

We’ll rely on these builtins and ideas throughout. Keep them handy.

- `getattr(obj, name, [default])` — read attribute by string name.
- `setattr(obj, name, value)` — set attribute by string name.
- `hasattr(obj, name)` — does lookup succeed?
- `delattr(obj, name)` — delete an attribute.
- `vars(obj)` — a dict of writable attributes (often `obj.__dict__`).
- `dir(obj)` — what’s available for attribute access (informal).
- `isinstance(x, T)` / `issubclass(C, B)` — type checks.
- `type(x)` — the _class_ of an object; `type(C)` is the _metaclass_ of `C`.

> Mental model: **attribute lookup** checks the instance, then the class, then base classes; descriptors can intercept.

---

## Mini demo: `getattr`/`setattr`

```python
class Box: pass
b = Box()
setattr(b, "value", 10)     # same as: b.value = 10
print(getattr(b, "value"))  # 10
print(hasattr(b, "missing"))# False
delattr(b, "value")         # removes attribute
```

Why useful? Because metaprogramming often works with _strings_ and _namespaces_.

---

## 1. Dynamic class creation with `type()`

Two faces of `type`:

```python
type(42)                        # -> <class 'int'>   (inspection)
Point = type("Point",           # -> a *new* class
             (object,),         # bases
             {"x": 0, "y": 0})  # namespace (class dict)
p = Point(); p.x, p.y           # 0, 0
```

- The **3‑arg** form constructs a class object on the fly.
- `type` is itself a class — the **default metaclass**.

---

## 1.1 Building progressively

Start from a plain dict, then add behavior:

```python
def shout(self): return f"{self.msg}!"

Greeter = type("Greeter", (object,), {"msg": "hi", "shout": shout})
g = Greeter()
assert g.shout() == "hi!"
```

- The functions you put in the namespace become methods (Python binds `self`).

---

## 2. How a `class` statement really runs

When Python executes:

```python
class Spam(Ham):
    RATE = 1.2
    def area(self, w, h): return w * h
```

It roughly does:

1. Choose a metaclass (default = `type` unless you specify `metaclass=`).
2. Call `Meta.__prepare__(name, bases, **kw)` → provides the mapping for the class body.
3. Execute the class body in that mapping (produces a dict of attrs).
4. Call `Meta.__new__(mcls, name, bases, namespace, **kw)` → _create_ class object.
5. Call `Meta.__init__(cls, name, bases, namespace, **kw)` → _post‑init_ class.
6. Bind class object to `Spam` in the surrounding scope.

---

## 2.1 Visual: class creation flow

```
class body ─► namespace dict ─► Meta.__new__ ─► class object ─► Meta.__init__ ─► Spam
                 ▲
                 └─ Meta.__prepare__ (optional dict-like with custom behavior)
```

---

## 3. Instance lifecycle: `__new__` vs `__init__`

```python
class Demo:
    def __new__(cls, *a, **k):
        print("ALLOCATE"); return super().__new__(cls)
    def __init__(self, *a, **k):
        print("INITIALIZE")

Demo()
```

- `__new__` makes the instance (must return the object).
- `__init__` configures it (must return `None`).

> Metaclasses have their own `__new__/__init__` — they shape the **class** object.

---

## 4. Class decorators (often your first tool)

```python
def add_debug(cls):
    def debug(self, *a, **k):
        return {"class": type(self).__name__, "attrs": vars(self)}
    cls.debug = debug
    return cls

@add_debug
class Thing: pass

Thing().debug()  # {'class': 'Thing', 'attrs': {...}}
```

- Decorators run **after** the class exists; simple and composable.
- Great for registries, instrumentation, small tweaks.

---

## 4.1 `__init_subclass__`: hook subclasses without a metaclass

```python
class Base:
    registry = {}
    def __init_subclass__(cls, /, name=None, **kw):
        super().__init_subclass__(**kw)
        if name:
            if name in Base.registry: raise ValueError("duplicate")
            Base.registry[name] = cls

class A(Base, name="A"): pass
class B(Base, name="B"): pass

Base.registry  # {'A': <class ...>, 'B': <class ...>}
```

- Use when you need to react to subclass creation but don’t need full metaclass power.

---

## 5. Metaclasses: the class of a class

```python
class Meta(type):
    def __new__(mcls, name, bases, ns, **kw):
        ns["UPPERED"] = {k for k in ns if k.isupper()}
        return super().__new__(mcls, name, bases, ns)

class Example(metaclass=Meta):
    RATE = 1.2
    def area(self, w, h): return w * h

type(Example) is Meta  # True
```

- Metaclasses let you **control class creation** and even **instance creation** via `__call__`.

---

## 5.1 Metaclass hooks in detail

- `__prepare__(name, bases, **kw)` → return a dict‑like for the class body.
- `__new__(mcls, name, bases, ns, **kw)` → build the class object.
- `__init__(cls, name, bases, ns, **kw)` → finalize the class.
- `__call__(cls, *a, **k)` → controls how instances are constructed.

```python
class Trace(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        print("PREPARE", name); return {}
    def __new__(mcls, name, bases, ns, **kw):
        print("NEW", name); return super().__new__(mcls, name, bases, ns)
    def __init__(cls, name, bases, ns, **kw):
        print("INIT", name); super().__init__(name, bases, ns)
    def __call__(cls, *a, **k):
        print("CALL", cls.__name__); return super().__call__(*a, **k)
```

---

## 5.2 Choosing the right tool

| **Decorator** (post‑create) | **`__init_subclass__`** (on subclass) | **Metaclass** (full control)                   |
| :-------------------------- | :------------------------------------ | :--------------------------------------------- |
| Small tweaks, registries    | Register/validate subclasses          | Transform namespace, control instance creation |
| Composable & simple         | Simple & local                        | One per hierarchy (composition is tricky)      |

**Rule**: Start simple; escalate only if you need **creation-time** or **instantiation-time** control.

---

## 6. Pattern 1: Plugin registry (decorator → metaclass)

### Step 1 — Decorator

```python
registry = {}

def register(cls=None, *, name=None):
    def decorate(c):
        key = (name or getattr(c, "plugin_name", c.__name__)).lower()
        if key in registry: raise ValueError("duplicate")
        registry[key] = c
        return c
    return decorate if cls is None else decorate(cls)
```

### Step 2 — Metaclass lift

```python
class PluginMeta(type):
    def __init__(cls, name, bases, ns, **kw):
        super().__init__(name, bases, ns)
        if ns.get("__abstract__", False): return
        key = getattr(cls, "plugin_name", name).lower()
        if key in registry and registry[key] is not cls: raise ValueError("duplicate")
        registry[key] = cls

class BasePlugin(metaclass=PluginMeta): __abstract__ = True
```

---

## 6.1 Try it

```python
@register
class Upper(BasePlugin):
    def transform(self, s): return s.upper()

class Emoji(BasePlugin):
    plugin_name = "emoji"
    def transform(self, s): return f"✨{s}✨"

list(registry)  # ['upper', 'emoji'] (order not guaranteed)
```

---

## 7. Pattern 2: Strict data container (`StrictStruct`)

**Goal:** Given annotations, auto‑generate `__slots__`, `__init__`, `__repr__`, and simple type checks.

### Outline

1. Merge `__annotations__` from bases and class.
2. Collect class‑level defaults.
3. Inject `__slots__ = tuple(fields)` and remove class‑level default attrs from the namespace (avoid shadowing).
4. Build methods:
   - `__init__(self, *args, **kwargs)` (positional in declared order; fill defaults; type check)
   - `__setattr__` (type check + forbid unknown names)
   - `__repr__` (debug-friendly)

---

## 7.1 Minimal type checks

Keep it simple for the lab: only builtin scalars (`int`, `float`, `bool`, `str`, `bytes`)—enough to practice the pattern without building Pydantic.

---

## 7.2 Example

```python
class Character(StrictStruct):
    name: str
    level: int = 1

a = Character("Ada")
a.level = 3      # OK
a.hp = 10        # AttributeError
Character(level="oops")  # TypeError
```

---

## 8. Pattern 3: Control instance creation with `metaclass.__call__`

What `type.__call__` roughly does:

1. `obj = cls.__new__(cls, *a, **k)`
2. if `isinstance(obj, cls)`: call `cls.__init__(obj, *a, **k)`
3. return `obj`

**Override it** to build singletons, multitons, pools, or instrument construction.

---

## 8.1 Multiton cache (by args)

```python
import weakref, threading

class ArgsCacheMeta(type):
    def __init__(cls, name, bases, ns, **kw):
        super().__init__(name, bases, ns)
        cls._cache = weakref.WeakValueDictionary()
        cls._lock = threading.RLock()
    def _key(cls, args, kwargs):
        return (tuple(args), tuple(sorted(kwargs.items())))  # requires hashable args
    def __call__(cls, *a, **k):
        key = cls._key(a, k)
        with cls._lock:
            found = cls._cache.get(key)
            if found is not None: return found
            obj = super().__call__(*a, **k)
            cls._cache[key] = obj
            return obj
```

---

## 8.2 Demo

```python
class Database(metaclass=ArgsCacheMeta):
    def __init__(self, url, timeout=30):
        self.url = url; self.timeout = timeout

a = Database("sqlite:///db.sqlite3", timeout=10)
b = Database("sqlite:///db.sqlite3", timeout=10)
c = Database("sqlite:///db.sqlite3", timeout=20)
assert a is b and a is not c
```

---

## 9. Advanced: attribute lookup order (simplified)

When accessing `obj.attr`:

1. If `type(obj)` defines a **data descriptor** named `attr`, use its `__get__`.
2. Else, if `attr` in `obj.__dict__`, return that.
3. Else, look in `type(obj)` and then its bases (MRO).
4. A non‑data descriptor’s `__get__` may run when found on the class.
5. If all fail, `__getattr__` (on the class) is a last‑chance hook.

> You usually don’t need descriptors for this module, but it explains why slots and type checks work the way they do.

---

## 10. Debugging toolbox

- Print from hooks: `__prepare__`, `__new__`, `__init__`, `__call__`.
- Inspect: `cls.__mro__`, `cls.__dict__.keys()`, `vars(obj)`, `dir(obj)`.
- `inspect.getsource(func)` to see generated code; `dis.dis(func)` if you’re curious.

---

## 11. Pitfalls & guidelines

- Prefer decorator/`__init_subclass__` when possible; metaclasses compose poorly.
- Keep metaclass logic small and testable; use pure helpers to transform namespaces.
- Document the contract your metaclass enforces; magic needs signage.
- Consider `dataclasses`, `attrs`, or Pydantic when your goal is data modeling and validation.

---

## Checkpoint quiz (quick)

1. What’s the difference between `__new__` and `__init__`?
2. When would a class decorator be preferable to a metaclass?
3. What does `metaclass.__call__` allow you to control?

_(Answers on the next slide)_

---

## Quiz answers

1. `__new__` allocates (returns the instance); `__init__` initializes (returns None).
2. When you need simple post‑creation tweaks; decorate many classes without changing MRO.
3. The **instance creation** process: you can add caching, pooling, instrumentation, etc.

---

## Labs lineup (reminder)

- **Lab A** — Decorator → metaclass registry (20 min)
- **Lab B** — `StrictStruct` data container (30 min)
- **Lab C** — Multiton cache with `__call__` (25 min)
- **Bonus** — `AutoPropMeta` properties (optional)

---

## Summary

- Classes are objects; metaclasses are classes of classes.
- You can create classes dynamically with `type` or the class statement protocol.
- Pick the simplest tool; only escalate to metaclasses when needed.
- Patterns practiced: registry, strict struct, multiton.

**You now have a mental model + patterns + exercises.**
