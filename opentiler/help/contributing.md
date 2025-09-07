# Contributing to OpenTiler

OpenTiler welcomes contributions — features, bug fixes, docs, examples, and plugins.

## Quick Start
- Install dev deps: `pip install -r requirements-dev.txt`
- Editable install: `pip install -e .`
- Run: `python main.py` or `opentiler`
- Test: `pytest -q` (GUI tests run offscreen)

## Guidelines
- Style: PEP 8, format with `black`, imports via `isort`, lint with `flake8`.
- Types: prefer type hints; run `mypy opentiler`.
- Tests: add/adjust tests for changes; use markers (`gui`, `integration`, `slow`).
- PRs: keep focused; include description, steps to test, and screenshots for UI.

## Commit Messages
Use `type(scope): short description` (e.g., `feat(export): add SVG`).

## Plugins
See `plugins/README.md` for architecture, hooks, and examples.

---

Full guide: `docs/CONTRIBUTING.md` and `docs/developer/DEVELOPER_MANUAL.md`.

Contributors: Get your name listed by adding features, fixing bugs, improving docs, or creating a useful plugin.
