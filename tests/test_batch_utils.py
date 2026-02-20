"""Tests for the shared batch polling helper."""

from __future__ import annotations

import threading
import time
from unittest.mock import Mock

import pytest

from veritail.batch_utils import (
    BatchCancelledError,
    poll_multiple_batches,
    poll_until_done,
)
from veritail.llm.client import LLMClient


def _make_client(**overrides) -> Mock:
    client = Mock(spec=LLMClient)
    client.batch_error_message.return_value = None
    for k, v in overrides.items():
        setattr(client, k, v)
    return client


class TestPollUntilDone:
    def test_poll_completed_immediately(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("completed", 5, 5)
        # Should not raise
        poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)
        client.poll_batch.assert_called_once_with("batch-1")

    def test_poll_after_in_progress(self) -> None:
        client = _make_client()
        client.poll_batch.side_effect = [
            ("in_progress", 1, 5),
            ("in_progress", 3, 5),
            ("completed", 5, 5),
        ]
        poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)
        assert client.poll_batch.call_count == 3

    def test_poll_failed_raises(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("failed", 0, 5)
        with pytest.raises(RuntimeError, match="batch-1 failed"):
            poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)

    def test_poll_expired_raises(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("expired", 3, 5)
        with pytest.raises(RuntimeError, match="batch-1 expired"):
            poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)

    def test_poll_error_includes_detail(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("failed", 0, 5)
        client.batch_error_message.return_value = "Rate limit exceeded"
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)

    def test_poll_error_without_detail(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("failed", 0, 5)
        client.batch_error_message.return_value = None
        with pytest.raises(RuntimeError, match="dashboard"):
            poll_until_done(client, "batch-1", expected_total=5, poll_interval=0)

    def test_poll_cancel_pre_set(self) -> None:
        """Cancel event already set before calling — raises immediately."""
        client = _make_client()
        client.poll_batch.return_value = ("in_progress", 0, 5)
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(BatchCancelledError):
            poll_until_done(
                client,
                "batch-1",
                expected_total=5,
                poll_interval=0,
                cancel_event=cancel,
            )
        # Cancel is checked before poll_batch, so at most one call
        assert client.poll_batch.call_count <= 1

    def test_poll_cancel_wakes_quickly(self) -> None:
        """Cancel event wakes the sleep within milliseconds, not poll_interval."""
        client = _make_client()
        client.poll_batch.return_value = ("in_progress", 0, 5)
        cancel = threading.Event()
        # Set cancel after 0.1s
        timer = threading.Timer(0.1, cancel.set)
        timer.start()
        t0 = time.monotonic()
        with pytest.raises(BatchCancelledError):
            poll_until_done(
                client,
                "batch-1",
                expected_total=5,
                poll_interval=300,
                cancel_event=cancel,
            )
        elapsed = time.monotonic() - t0
        assert elapsed < 5.0  # Must not wait 300s

    def test_poll_cancel_event_none_unchanged(self) -> None:
        """cancel_event=None with completed status works as before."""
        client = _make_client()
        client.poll_batch.return_value = ("completed", 5, 5)
        poll_until_done(
            client, "batch-1", expected_total=5, poll_interval=0, cancel_event=None
        )
        client.poll_batch.assert_called_once_with("batch-1")


class TestPollMultipleBatches:
    def test_both_succeed(self) -> None:
        client = _make_client()
        client.poll_batch.side_effect = [
            # First poll round: both in progress
            ("in_progress", 2, 5),
            ("in_progress", 1, 3),
            # Second poll round: first completes, second still in progress
            ("completed", 5, 5),
            ("in_progress", 2, 3),
            # Third poll round: second completes
            ("completed", 3, 3),
        ]
        poll_multiple_batches(
            client,
            [
                ("batch-rel", 5, "Relevance batch"),
                ("batch-corr", 3, "Correction batch"),
            ],
            poll_interval=0,
        )
        assert client.poll_batch.call_count == 5

    def test_one_fails(self) -> None:
        client = _make_client()
        client.poll_batch.side_effect = [
            ("in_progress", 2, 5),
            ("failed", 0, 3),
        ]
        with pytest.raises(RuntimeError, match="batch-corr failed"):
            poll_multiple_batches(
                client,
                [
                    ("batch-rel", 5, "Relevance batch"),
                    ("batch-corr", 3, "Correction batch"),
                ],
                poll_interval=0,
            )

    def test_single_entry(self) -> None:
        """Single-entry list behaves like poll_until_done."""
        client = _make_client()
        client.poll_batch.return_value = ("completed", 5, 5)
        poll_multiple_batches(
            client,
            [("batch-1", 5, "My batch")],
            poll_interval=0,
        )
        client.poll_batch.assert_called_once_with("batch-1")

    def test_empty_list(self) -> None:
        """Empty batch list returns immediately."""
        client = _make_client()
        poll_multiple_batches(client, [], poll_interval=0)
        client.poll_batch.assert_not_called()

    def test_error_includes_detail(self) -> None:
        client = _make_client()
        client.poll_batch.return_value = ("failed", 0, 5)
        client.batch_error_message.return_value = "Token limit exceeded"
        with pytest.raises(RuntimeError, match="Token limit exceeded"):
            poll_multiple_batches(
                client,
                [("batch-1", 5, "My batch")],
                poll_interval=0,
            )

    def test_poll_multiple_cancel(self) -> None:
        """Pre-set cancel event raises BatchCancelledError."""
        client = _make_client()
        client.poll_batch.return_value = ("in_progress", 0, 5)
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(BatchCancelledError):
            poll_multiple_batches(
                client,
                [("batch-1", 5, "My batch")],
                poll_interval=0,
                cancel_event=cancel,
            )
