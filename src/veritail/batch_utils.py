"""Shared polling helper for batch evaluation pipelines."""

from __future__ import annotations

import time

from rich.console import Console
from rich.progress import Progress

from veritail.llm.client import LLMClient

console = Console()


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
                raise RuntimeError(msg)

            time.sleep(poll_interval)
