"""Evaluation backend interface and factory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from veritail.types import JudgmentRecord


class EvalBackend(ABC):
    """Abstract base class for evaluation storage backends."""

    @abstractmethod
    def log_judgment(self, judgment: JudgmentRecord) -> None:
        """Store an LLM judgment (trace + score + reasoning)."""
        ...

    @abstractmethod
    def log_experiment(self, name: str, config: dict[str, Any]) -> None:
        """Register an experiment run with its configuration."""
        ...

    @abstractmethod
    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Retrieve all LLM judgments for an experiment."""
        ...


def create_backend(backend_type: str, **kwargs: Any) -> EvalBackend:
    """Create an evaluation backend by type name.

    Args:
        backend_type: "file" or "langfuse"
        **kwargs: Backend-specific configuration

    Returns:
        An initialized EvalBackend instance.
    """
    if backend_type == "file":
        from veritail.backends.file import FileBackend

        return FileBackend(**kwargs)
    elif backend_type == "langfuse":
        try:
            from veritail.backends.langfuse import LangfuseBackend
        except ImportError:
            raise ImportError(
                "Langfuse backend requires the langfuse extra. "
                "Install with: pip install veritail[langfuse]"
            )
        return LangfuseBackend(**kwargs)
    else:
        raise ValueError(
            f"Unknown backend type: {backend_type}. Use 'file' or 'langfuse'."
        )


__all__ = ["EvalBackend", "create_backend"]
