"""Report generation for evaluation results."""

from search_eval.reporting.comparison import generate_comparison_report
from search_eval.reporting.single import generate_single_report

__all__ = ["generate_single_report", "generate_comparison_report"]
