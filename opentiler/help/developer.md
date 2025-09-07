# Developer Guide (In-App Summary)

This is a short in-app summary. For the full guide, see repo `docs/developer/DEVELOPER_MANUAL.md`.

## Build & Run
- Install dev deps: `pip install -r requirements-dev.txt`
- Editable install: `pip install -e .`
- Run: `python main.py` or `opentiler`
- Tests: `pytest -q` (GUI tests run offscreen)

## Coding Style
- Python 3.8+, PEP 8, black, isort, flake8, mypy.
- Names: snake_case for funcs, CamelCase for classes.

## Plugins
- See `plugins/` for plugin manager, hooks, builtins.
- Start with `plugins/README.md`.

### Plugin Basics
- Base class: `plugins/base_plugin.py` defines the plugin interface and lifecycle.
- Manager: `plugins/plugin_manager.py` discovers, loads, and manages plugins.
- Hooks: `plugins/hook_system.py` exposes before/after hooks for key app events.
- Registry: `plugins/plugin_registry.py` tracks metadata/dependencies.
- UI: `plugins/plugin_manager_ui.py` integrates management into Settings.

Typical plugin skeleton:
```python
from plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    name = "My Plugin"
    version = "0.1.0"

    def on_load(self):
        # Register menu actions, hooks, etc.
        pass

    def on_unload(self):
        # Cleanup any resources
        pass
```

Registering hooks (example):
```python
from plugins.hook_system import Hooks

def on_after_document_load(ctx):
    # Inspect/adjust state after a document loads
    pass

plugin.register_hook(Hooks.AFTER_DOCUMENT_LOAD, on_after_document_load, priority=50)
```

See the full guide in `docs/developer/DEVELOPER_MANUAL.md` and `plugins/README.md`.

## Contributing
- Keep PRs focused. Pass lint/format/types/tests.
