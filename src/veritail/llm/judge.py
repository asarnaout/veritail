"""LLM-based relevance judgment for query-result pairs."""

from __future__ import annotations

import re
from collections.abc import Callable

from veritail.llm.client import LLMClient
from veritail.types import JudgmentRecord, SearchResult


class RelevanceJudge:
    """Judges the relevance of search results to queries using an LLM."""

    def __init__(
        self,
        client: LLMClient,
        system_prompt: str,
        format_user_prompt: Callable[[str, SearchResult], str],
        experiment: str,
    ) -> None:
        self._client = client
        self._system_prompt = system_prompt
        self._format_user_prompt = format_user_prompt
        self._experiment = experiment

    def judge(
        self,
        query: str,
        result: SearchResult,
        *,
        query_type: str | None = None,
    ) -> JudgmentRecord:
        """Judge the relevance of a single search result to a query."""
        user_prompt = self._format_user_prompt(query, result)
        response = self._client.complete(self._system_prompt, user_prompt)

        score, attribute_verdict, reasoning = self._parse_response(response.content)

        return JudgmentRecord(
            query=query,
            product=result,
            score=score,
            reasoning=reasoning,
            attribute_verdict=attribute_verdict,
            model=response.model,
            experiment=self._experiment,
            query_type=query_type,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )

    @staticmethod
    def _parse_response(response_text: str) -> tuple:
        """Parse the LLM response to extract score, attribute verdict, and reasoning.

        Expected format:
            SCORE: <0-3>
            ATTRIBUTES: <match|partial|mismatch|n/a>
            REASONING: <brief justification text>
        """
        # Extract score
        score_match = re.search(r"(?i)SCORE\s*[:=]\s*(\d)", response_text)
        if not score_match:
            raise ValueError(
                f"Could not parse score from LLM response. "
                f"Expected 'SCORE: <0-3>'. Got:\n{response_text}"
            )

        score = int(score_match.group(1))
        if score not in (0, 1, 2, 3):
            raise ValueError(
                f"Score must be 0, 1, 2, or 3. Got: {score}. "
                f"Response:\n{response_text}"
            )

        # Extract attribute verdict (default to "n/a" for custom rubrics)
        attr_match = re.search(
            r"ATTRIBUTES:\s*(\w[\w/ ]*?)(?:\n|$)", response_text
        )
        attribute_verdict = (
            attr_match.group(1).strip().lower() if attr_match else "n/a"
        )

        # Extract reasoning
        reasoning_match = re.search(
            r"REASONING:\s*(.*)", response_text, re.DOTALL
        )
        reasoning = (
            reasoning_match.group(1).strip() if reasoning_match else ""
        )

        return score, attribute_verdict, reasoning
