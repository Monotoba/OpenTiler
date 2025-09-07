# Contributing to OpenTiler

Thanks for your interest in improving OpenTiler! Contributions of all kinds are welcome — features, bug fixes, documentation, examples, and plugins.

## Getting Started
- Fork the repository on GitHub and create a feature branch: `git checkout -b feat/your-feature`.
- Install dev requirements: `pip install -r requirements-dev.txt`.
- Editable install for local development: `pip install -e .`.
- Run the app: `python main.py` or `opentiler`.
- Run tests: `pytest -q` (GUI tests run offscreen).

## Development Guidelines
- Style: Python 3.8+, PEP 8, 4-space indent. Format with `black .`, sort imports with `isort .`, lint with `flake8`.
- Types: prefer type hints; run `mypy opentiler`.
- Tests: add or update tests for your changes. Use markers (`gui`, `integration`, `slow`) as appropriate.
- Docs: update user/dev docs and in-app help when behavior changes.
- Scope: keep PRs focused; include a clear description and steps to test.

## Commit Messages
Use conventional style: `type(scope): short description`.

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

Example:
```
feat(export): add SVG exporter

- Implement SVGExporter
- Add option to export dialog
- Include unit tests
```

## Plugins
- See `plugins/README.md` for the plugin architecture, hooks, and examples.
- Start with a minimal plugin derived from `plugins/base_plugin.py` and register hooks you need.

## Opening a Pull Request
- Ensure tests pass locally: `pytest -q` (or with coverage: `pytest --cov=opentiler`).
- Ensure formatting/lint/type checks pass.
- Reference related issues and include screenshots/GIFs for UI changes.
- Note risks or migration considerations.

## Code of Conduct
Be respectful and constructive. We value helpful reviews and welcoming collaboration.

## Getting Your Name Listed
Contributors are recognized in the app’s About dialog. Get your name listed by adding features, fixing bugs, improving docs, or creating a useful plugin.

---

For deeper details, see `docs/developer/DEVELOPER_MANUAL.md` and `docs/README.md`.
