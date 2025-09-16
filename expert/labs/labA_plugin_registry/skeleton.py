from __future__ import annotations

registry: dict[str, type] = {}

def register(cls=None, *, name: str | None = None):
    """Register a class in the global registry under a name.

    Usage:
        @register
        class Foo: ...
        # or
        @register(name="bar")
        class Foo: ...
    """
    # TODO: implement (support bare and with-args usage)
    raise NotImplementedError

def discover() -> list[str]:
    """Return the sorted list of registered plugin names."""
    # TODO
    raise NotImplementedError

class PluginMeta(type):
    # TODO: implement registration in __init__; skip if __abstract__ is True
    pass

class BasePlugin(metaclass=PluginMeta):
    __abstract__ = True
    # Optional: subclasses may set plugin_name = "alias"
    def apply(self, image, **opts):  # pragma: no cover
        raise NotImplementedError

# Example usage once implemented:
# @register(name="resize")
# class Resize(BasePlugin): ...
