# Tests for Lab 1 — run with: pytest -q
import importlib.util, os, sys

HERE = os.path.dirname(__file__)

def load_module(name):
    path = os.path.join(HERE, name)
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

def test_decorator_register_and_discover():
    m = load_module("solution.py")
    assert isinstance(m.registry, dict)
    # ensure our example plugins are there
    assert set(m.discover()) >= {"resize", "crop", "emoji"}

def test_duplicate_detection():
    m = load_module("solution.py")
    import pytest
    with pytest.raises(ValueError):
        @m.register(name="resize")
        class Again(m.BasePlugin):
            def apply(self, image, **opts): return image
