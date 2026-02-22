"""Centralized logging configuration for veritail."""

from __future__ import annotations

import logging
import sys

_FORMAT = "%(levelname).1s %(name)s: %(message)s"


def configure_logging(*, verbose: bool) -> None:
    """Configure the ``veritail`` namespace logger.

    Call once from the CLI entry-point.  When *verbose* is ``True`` the
    root ``"veritail"`` logger is set to DEBUG and a stderr handler is
    attached; otherwise the level stays at WARNING (silent by default).

    Re-entrant: clears existing handlers before adding a new one so that
    repeated calls (e.g. in tests) don't duplicate output.
    """
    logger = logging.getLogger("veritail")
    logger.handlers.clear()

    level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(handler)
