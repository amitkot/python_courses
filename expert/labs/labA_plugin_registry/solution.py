from __future__ import annotations
from typing import Callable, TypeVar

T = TypeVar("T", bound=type)
registry: dict[str, type] = {}

def _key_of(c: type, name: str | None) -> str:
    key = (name or getattr(c, "plugin_name", c.__name__)).strip()
    if not key:
        raise ValueError("Empty plugin name")
    return key

def register(cls: T | None = None, *, name: str | None = None):
    def decorate(c: T) -> T:
        key = _key_of(c, name)
        if key in registry:
            raise ValueError(f"Duplicate plugin name: {key!r}")
        registry[key] = c
        return c
    return decorate if cls is None else decorate(cls)

def discover() -> list[str]:
    return sorted(registry.keys())

class PluginMeta(type):
    def __init__(cls, name, bases, ns, **kw):
        super().__init__(name, bases, ns)
        if ns.get("__abstract__", False):
            return
        key = _key_of(cls, getattr(cls, "plugin_name", None))
        if key in registry and registry[key] is not cls:
            raise ValueError(f"Duplicate plugin name: {key!r}")
        registry[key] = cls

class BasePlugin(metaclass=PluginMeta):
    __abstract__ = True
    def apply(self, image, **opts):
        raise NotImplementedError

# Demo plugins for the CLI image tool idea
@register(name="resize")
class Resize(BasePlugin):
    def apply(self, image, **opts):
        w = opts.get("width"); h = opts.get("height")
        return f"RESIZED({image}) to {w}x{h}"

@register(name="crop")
class Crop(BasePlugin):
    def apply(self, image, **opts):
        x,y,w,h = opts.get("x",0), opts.get("y",0), opts.get("w",10), opts.get("h",10)
        return f"CROPPED({image}) at ({x},{y}) size {w}x{h}"

class Emoji(BasePlugin):
    plugin_name = "emoji"
    def apply(self, image, **opts):
        return f"✨{image}✨"

if __name__ == "__main__":
    print("Plugins:", discover())
    print(registry["resize"]().apply("img.jpg", width=100, height=80))
