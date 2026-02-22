"""Tests for veritail.logging configuration."""

from __future__ import annotations

import logging
import sys

from veritail.logging import configure_logging


def test_default_level_is_warning() -> None:
    """Without verbose, the veritail logger should be WARNING."""
    configure_logging(verbose=False)
    logger = logging.getLogger("veritail")
    assert logger.level == logging.WARNING


def test_verbose_enables_debug() -> None:
    """With verbose, the veritail logger should be DEBUG."""
    configure_logging(verbose=True)
    logger = logging.getLogger("veritail")
    assert logger.level == logging.DEBUG


def test_child_loggers_inherit() -> None:
    """Child loggers like veritail.pipeline should inherit the level."""
    configure_logging(verbose=True)
    child = logging.getLogger("veritail.pipeline")
    assert child.getEffectiveLevel() == logging.DEBUG


def test_handler_writes_to_stderr() -> None:
    """The handler should target stderr, not stdout."""
    configure_logging(verbose=True)
    logger = logging.getLogger("veritail")
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stderr  # type: ignore[attr-defined]


def test_reconfigure_clears_old_handlers() -> None:
    """Calling configure_logging twice should not duplicate handlers."""
    configure_logging(verbose=True)
    configure_logging(verbose=False)
    logger = logging.getLogger("veritail")
    assert len(logger.handlers) == 1


def test_log_format(capfd: object) -> None:
    """Debug messages should use the 'D veritail.x: msg' format."""
    configure_logging(verbose=True)
    child = logging.getLogger("veritail.test_module")
    child.debug("hello world")

    # capfd captures fd-level stderr (works for logging StreamHandler)
    captured = capfd.readouterr()  # type: ignore[union-attr]
    assert "D veritail.test_module: hello world" in captured.err
