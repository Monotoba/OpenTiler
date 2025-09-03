"""
Application logging utilities for OpenTiler.

Minimal refactor: centralize logging configuration and provide
component-aware filtering based on settings.
"""

import logging
from typing import Optional

try:
    # Use the global config instance
    from ..settings.config import config as app_config
except Exception:  # pragma: no cover
    app_config = None


COMPONENTS = {
    'printing',
    'projects',
    'preview',
    'viewer',
    'export',
    'metadata',
    'settings',
}


class ComponentFilter(logging.Filter):
    """Filter records by component enablement from settings.

    If logging is globally disabled, only ERROR+ records are allowed to pass.
    If component is disabled, WARNING+ records are allowed; DEBUG/INFO are dropped.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        if app_config is None:
            return True

        enabled = _safe_bool(app_config.get("logging_enabled", False))
        if not enabled:
            # Allow only errors/critical through when disabled
            return record.levelno >= logging.ERROR

        component = getattr(record, 'component', None)
        if not component:
            return True

        # Per-component toggle names: logging_<component>
        key = f"logging_{component}"
        comp_enabled = _safe_bool(app_config.get(key, True))

        if comp_enabled:
            return True
        # Component disabled: allow warnings and above
        return record.levelno >= logging.WARNING


def _safe_bool(value) -> bool:
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)


def configure_from_config(conf=None, handler: Optional[logging.Handler] = None) -> None:
    """Configure root application logger from settings.

    - Sets level from logging_level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    - Installs a StreamHandler with a concise format if none provided
    - Adds a ComponentFilter wired to settings
    """
    global app_config
    if conf is not None:
        app_config = conf

    level_name = (app_config.get("logging_level", "WARNING") if app_config else "WARNING")
    level = getattr(logging, str(level_name).upper(), logging.WARNING)

    logger = logging.getLogger('opentiler')
    logger.setLevel(level)

    # Ensure a single handler
    if handler is None:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('[%(levelname)s] %(component)s: %(message)s')
        handler.setFormatter(formatter)

    # Clear existing handlers to avoid duplication
    logger.handlers.clear()
    logger.addHandler(handler)
    # Attach component filter
    logger.addFilter(ComponentFilter())


def get_logger(component: str) -> logging.LoggerAdapter:
    """Get a component-tagged logger adapter."""
    base = logging.getLogger('opentiler')
    return logging.LoggerAdapter(base, extra={'component': component})

