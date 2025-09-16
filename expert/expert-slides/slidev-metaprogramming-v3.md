---
title: "Python Metaprogramming & Metaclasses — v3"
info: "Advanced Python In Depth · ~3 hours · single-concept slides with speaker notes"
theme: default
highlighter: shiki
lineNumbers: false
fonts:
  sans: Inter
  mono: Fira Code
---

# Python Metaprogramming & Metaclasses

Single‑concept slides · Labs included

<!--
Welcome! This deck is intentionally minimal on-screen and rich in presenter notes.
Click "P" in Slidev to open Presenter View (notes & timing).
-->

---

## Session Plan (You Say This)

- Part 1: Attribute model & dynamic classes
- Part 2: Decorators & subclass hooks
- Part 3: Metaclasses & patterns
- Labs: 1 (Registry), 2 (StrictStruct), 3 (Multiton)

<!--
Keep the pace: (~10) warm-up; (~25) type & class protocol; (20) Lab 1; (~20) hooks deep dive;
(30) Lab 2; (~15) metaclass __call__; (25) Lab 3; (5) wrap.
-->

---

## Warm‑up

**What is metaprogramming?**

<!--
Definition: Code that writes/changes code behavior. Examples: decorators, descriptors, metaclasses.
Ask: "Where have you seen it in the wild?" (ORMs, frameworks, APIs).
-->

---

## One Tool at a Time: `getattr`

```py
getattr(obj, "name", default)
```

- Read by string
- Optional default

<!--
Demo live:
class Box: pass; b=Box(); b.x=10; getattr(b,"x"); getattr(b,"missing",0).
Explain: metaprogramming often needs string-driven attribute access.
-->

---

## `setattr` and `delattr`

```py
setattr(obj, "x", 10)
delattr(obj, "x")
```

- Set/delete by string

<!--
Show why: dynamic loading of plugins, deserializers, config injection.
-->

---

## `vars()` and `dir()`

- `vars(obj)` → writable attributes
- `dir(obj)` → discoverability

<!--
vars(obj) is often obj.__dict__.
Use to inspect generated classes/instances during labs.
-->

---

## Lookup (Simplified Mental Model)

instance → class → bases

<!--
Keep it high-level; no descriptors yet.
Why it matters: where do attributes come from after metaclass transforms?
-->

---

## `type()` (inspect)

```py
type(42)  # <class 'int'>
```

- The class of an object

<!--
We use it to show that classes themselves are objects.
-->

---

## `type(name, bases, ns)` (create)

```py
Greeter = type("Greeter", (object,), {"msg": "hi"})
```

- Build a class dynamically

<!--
Add a method: {"shout": lambda self: self.msg + "!"}.
Point out method binding: Python inserts self automatically.
-->

---

## Mini Use Case

**Dynamic DTOs from JSON schema**

<!--
Explain mapping schema dict → type(name,bases,ns). Useful in testing and codegen.
-->

---

## Q&A (1 min)

- When do you reach for `getattr`?

<!--
Take 1-2 answers. Transition to the class statement protocol.
-->

---

## Class Statement: Big Picture

**A `class` statement creates a class object.**

<!--
We are about to peel the steps: prepare → body → new → init.
-->

---

## Step 1 — Resolve Metaclass

default: `type`

<!--
Only if you specify metaclass=... or inherit from a class with a custom metaclass.
-->

---

## Step 2 — `__prepare__`

Provide the mapping for class body

<!--
Used to customize the dict for the class body (order checking, validation, collection).
-->

---

## Step 3 — Execute Body

Fill the mapping with definitions

<!--
All methods/constants land in the namespace mapping. No heavy detail here.
-->

---

## Step 4 — `__new__`

Build the class object

<!--
Transform namespace; inject/modify attributes.
-->

---

## Step 5 — `__init__`

Finalize the class

<!--
Post-processing. Keep this lightweight.
-->

---

## Instance Lifecycle: `__new__` vs `__init__`

- `__new__`: allocate (return instance)
- `__init__`: initialize (return None)

<!--
Show a tiny print demo if needed. Contrast with metaclass hooks (later).
-->

---

## Q&A

- Where would you validate constructor inputs?

<!--
Answer: typically in __init__, sometimes in __setattr__ or factory methods. Keep __new__ minimal unless substituting instance.
-->

---

## Decorators First

**Class decorators modify a ready class.**

<!--
Pros: simple, composable. Great starting point for registries/instrumentation.
-->

---

## Example: `@add_debug`

```py
def add_debug(cls):
    def debug(self): return {"class": type(self).__name__, "attrs": vars(self)}
    cls.debug = debug; return cls
```

<!--
Attach one small behavior; low ceremony.
-->

---

## `__init_subclass__`

React to subclass creation

<!--
Great for lightweight frameworks: register subclasses, validate configs.
-->

---

## Lab 1 🧪 — Plugin Registry

Decorator → Metaclass

<!--
Direct students to /labs/labA_plugin_registry/README.md.
Goal: start with @register decorator, then lift into PluginMeta.__init__ for auto-registration.
Timebox: ~20 minutes.
-->

---

## Real-World Angle

**Plugins for a CLI image tool**
`resize`, `crop`, `emoji`

<!--
Tie registry pattern to DevEx: discover commands at runtime, keep core small.
-->

---

## Metaclasses

**The class of a class**

<!--
Now that they’ve built a registry, show how to move logic to metaclass hooks.
-->

---

## Hook: `__prepare__`

Return class-body mapping

<!--
Example: ordered mapping, name validation, field collection.
-->

---

## Hook: `__new__`

Transform namespace → create class

<!--
Where you usually inject methods like __repr__, __init__, slots.
-->

---

## Hook: `__init__`

Finalize class object

<!--
Avoid heavy work; run idempotent registration; store metadata.
-->

---

## Hook: `__call__`

Control instance creation

<!--
Use cases: singletons, multitons, connection pooling, instrumentation.
-->

---

## Q&A

- Why choose a metaclass over a decorator?

<!--
If you need to change creation time or instance construction (__call__), or enforce contracts at class level.
-->

---

## Lab 2 🧪 — `StrictStruct`

Annotations → slots, init, repr, type checks

<!--
Direct students to /labs/labB_strictstruct/README.md.
Focus: collecting annotations; defaults; inject methods. Keep types simple (int/float/str/bool/bytes).
Timebox: ~30 minutes.
-->

---

## Real-World Angle

**Config objects**
e.g., `ApiConfig(base_url: str, timeout: int=30)`

<!--
Shows how structured containers enforce correctness at boundaries without a heavy framework.
-->

---

## Controlling Instances: `metaclass.__call__`

Override to add caching/pooling

<!--
We'll build a multiton keyed by args/kwargs.
-->

---

## Lab 3 🧪 — Multiton Cache

One instance per `(args, kwargs)`

<!--
Direct to /labs/labC_multiton/README.md. Use WeakValueDictionary + RLock.
Timebox: ~25 minutes.
-->

---

## Real-World Angle

**Database connections / HTTP session pools**

<!--
Concrete mapping: same DSN → same object, fewer connections.
-->

---

## Debugging Quick Tips

- `vars(obj)`, `cls.__dict__`
- print in `__new__`, `__init__`, `__call__`

<!--
Encourage inspection during labs. Mention getsource() and dis() if asked.
-->

---

## Q&A

- What pitfalls have you hit so far?

<!--
Listen and diagnose; tie back to "prefer simpler tools" rule.
-->

---

## Summary (Say This)

- Start simple → decorator / `__init_subclass__`
- Use metaclasses when you need creation/instantiation control
- Patterns: registry, strict struct, multiton

<!--
Offer the cheat sheet and repo/zip.
-->
