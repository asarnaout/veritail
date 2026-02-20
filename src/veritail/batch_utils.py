"""Shared polling helper for batch evaluation pipelines."""

from __future__ import annotations

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


def poll_until_done(
    llm_client: LLMClient,
    batch_id: str,
    *,
    expected_total: int,
    poll_interval: int = 60,
    label: str = "Waiting for batch completion...",
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

            time.sleep(poll_interval)


def poll_multiple_batches(
    llm_client: LLMClient,
    batches: Sequence[tuple[str, int, str]],
    *,
    poll_interval: int = 60,
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
                time.sleep(poll_interval)
