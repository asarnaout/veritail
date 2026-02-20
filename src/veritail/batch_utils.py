"""Shared polling helper for batch evaluation pipelines."""

from __future__ import annotations

import threading
import time
from collections.abc import Sequence

from rich.console import Console
from rich.progress import Progress, TaskID

from veritail.llm.client import LLMClient

console = Console()


class BatchFailedError(RuntimeError):
    """A batch reached a terminal failure state (failed/expired)."""

    def __init__(self, message: str, *, batch_id: str, status: str) -> None:
        super().__init__(message)
        self.batch_id = batch_id
        self.status = status


class BatchCancelledError(Exception):
    """Raised when a polling loop is interrupted by a cancellation event.

    Does NOT extend ``RuntimeError`` so pipeline error handlers (which manage
    checkpoints) will not catch it.
    """

    def __init__(self, message: str = "Batch polling cancelled") -> None:
        super().__init__(message)


def poll_until_done(
    llm_client: LLMClient,
    batch_id: str,
    *,
    expected_total: int,
    poll_interval: int = 60,
    label: str = "Waiting for batch completion...",
    cancel_event: threading.Event | None = None,
) -> None:
    """Poll a batch until it reaches a terminal state.

    Raises ``RuntimeError`` on ``"failed"`` or ``"expired"`` status.
    The caller is responsible for checkpoint cleanup.
    """
    with Progress(console=console) as progress:
        poll_task = progress.add_task(
            f"[cyan]{label}",
            total=expected_total,
        )
        while True:
            if cancel_event is not None and cancel_event.is_set():
                raise BatchCancelledError()

            status, completed, total = llm_client.poll_batch(batch_id)
            progress.update(
                poll_task, completed=completed, total=total or expected_total
            )

            if status == "completed":
                break
            if status in ("failed", "expired"):
                detail = llm_client.batch_error_message(batch_id)
                msg = f"Batch {batch_id} {status}."
                if detail:
                    msg += f" Error: {detail}"
                else:
                    msg += " Check your provider's dashboard for details."
                raise BatchFailedError(msg, batch_id=batch_id, status=status)

            if cancel_event is not None:
                if cancel_event.wait(poll_interval):
                    raise BatchCancelledError()
            else:
                time.sleep(poll_interval)


def poll_multiple_batches(
    llm_client: LLMClient,
    batches: Sequence[tuple[str, int, str]],
    *,
    poll_interval: int = 60,
    cancel_event: threading.Event | None = None,
) -> None:
    """Poll multiple batches concurrently in a single Rich progress context.

    *batches* is a sequence of ``(batch_id, expected_total, label)`` tuples.
    Raises ``RuntimeError`` on the first failed/expired batch (matching the
    behaviour of :func:`poll_until_done`).
    """
    if not batches:
        return

    with Progress(console=console) as progress:
        tasks: list[tuple[str, int, TaskID]] = []
        for batch_id, expected_total, label in batches:
            tid = progress.add_task(f"[cyan]{label}", total=expected_total)
            tasks.append((batch_id, expected_total, tid))

        pending = set(range(len(tasks)))

        while pending:
            if cancel_event is not None and cancel_event.is_set():
                raise BatchCancelledError()

            for idx in list(pending):
                batch_id, expected_total, tid = tasks[idx]
                status, completed, total = llm_client.poll_batch(batch_id)
                progress.update(tid, completed=completed, total=total or expected_total)

                if status == "completed":
                    pending.discard(idx)
                elif status in ("failed", "expired"):
                    detail = llm_client.batch_error_message(batch_id)
                    msg = f"Batch {batch_id} {status}."
                    if detail:
                        msg += f" Error: {detail}"
                    else:
                        msg += " Check your provider's dashboard for details."
                    raise BatchFailedError(msg, batch_id=batch_id, status=status)

            if pending:
                if cancel_event is not None:
                    if cancel_event.wait(poll_interval):
                        raise BatchCancelledError()
                else:
                    time.sleep(poll_interval)
