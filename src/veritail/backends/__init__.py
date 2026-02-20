"""Evaluation backend interface and factory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from veritail.types import CorrectionJudgment, JudgmentRecord, SuggestionJudgment


class EvalBackend(ABC):
    """Abstract base class for evaluation storage backends."""

    @abstractmethod
    def log_judgment(self, judgment: JudgmentRecord) -> None:
        """Store an LLM judgment (trace + score + reasoning)."""
        ...

    @abstractmethod
    def log_experiment(
        self, name: str, config: dict[str, Any], *, resume: bool = False
    ) -> None:
        """Register an experiment run with its configuration."""
        ...

    @abstractmethod
    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Retrieve all LLM judgments for an experiment."""
        ...

    def log_correction_judgment(self, judgment: CorrectionJudgment) -> None:
        """Optionally store a correction judgment. Default no-op."""
        pass

    def log_suggestion_judgment(self, judgment: SuggestionJudgment) -> None:
        """Optionally store a suggestion judgment. Default no-op."""
        pass

    def get_completed_query_indices(self, experiment: str) -> set[int]:
        """Return the set of query indices already judged for *experiment*."""
        return set()


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
        except Exception as exc:
            raise ImportError(
                f"Failed to load the Langfuse backend: {exc}. "
                "This is typically caused by a Langfuse SDK incompatibility "
                "with your Python version. Try Python 3.13 or earlier, "
                "or check for a newer langfuse release."
            ) from exc
        return LangfuseBackend(**kwargs)
    else:
        raise ValueError(
            f"Unknown backend type: {backend_type}. Use 'file' or 'langfuse'."
        )


__all__ = ["EvalBackend", "create_backend"]
