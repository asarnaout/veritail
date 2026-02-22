"""LLM-based semantic evaluation for autocomplete suggestions."""

from __future__ import annotations

import re

from veritail.llm.client import BatchRequest, LLMClient, LLMResponse
from veritail.prompts import load_prompt
from veritail.types import SuggestionJudgment

SUGGESTION_SYSTEM_PROMPT = load_prompt("autocomplete/suggestion.md")


class SuggestionJudge:
    """Judges autocomplete suggestion quality using an LLM."""

    def __init__(
        self,
        client: LLMClient,
        system_prompt: str,
        experiment: str,
    ) -> None:
        self._client = client
        self._system_prompt = system_prompt
        self._experiment = experiment

    def judge(
        self,
        prefix: str,
        suggestions: list[str],
    ) -> SuggestionJudgment:
        """Judge the quality of suggestions for a single prefix."""
        user_prompt = self._format_user_prompt(prefix, suggestions)
        response = self._client.complete(self._system_prompt, user_prompt)

        relevance, diversity, flagged, reasoning = self._parse_response(
            response.content
        )

        return SuggestionJudgment(
            prefix=prefix,
            suggestions=suggestions,
            relevance_score=relevance,
            diversity_score=diversity,
            flagged_suggestions=flagged,
            reasoning=reasoning,
            model=response.model,
            experiment=self._experiment,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )

    def prepare_request(
        self,
        custom_id: str,
        prefix: str,
        suggestions: list[str],
    ) -> BatchRequest:
        """Build a BatchRequest for a single prefix evaluation."""
        user_prompt = self._format_user_prompt(prefix, suggestions)
        return BatchRequest(
            custom_id=custom_id,
            system_prompt=self._system_prompt,
            user_prompt=user_prompt,
        )

    def parse_batch_result(
        self,
        response: LLMResponse,
        prefix: str,
        suggestions: list[str],
    ) -> SuggestionJudgment:
        """Parse a batch response into a SuggestionJudgment."""
        relevance, diversity, flagged, reasoning = self._parse_response(
            response.content
        )
        return SuggestionJudgment(
            prefix=prefix,
            suggestions=suggestions,
            relevance_score=relevance,
            diversity_score=diversity,
            flagged_suggestions=flagged,
            reasoning=reasoning,
            model=response.model,
            experiment=self._experiment,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )

    @staticmethod
    def _format_user_prompt(prefix: str, suggestions: list[str]) -> str:
        """Build a numbered suggestion list for the LLM."""
        lines = [f"## Prefix\n{prefix}\n", "## Suggestions"]
        for i, s in enumerate(suggestions, 1):
            lines.append(f"{i}. {s}")
        return "\n".join(lines)

    @staticmethod
    def _parse_response(
        response_text: str,
    ) -> tuple[int, int, list[str], str]:
        """Parse relevance, diversity, flagged list, and reasoning from LLM response.

        Expected format:
            RELEVANCE: <0-3>
            DIVERSITY: <0-3>
            FLAGGED: <comma-separated list or "none">
            REASONING: <brief justification>
        """
        # Extract relevance score
        relevance_match = re.search(r"(?i)RELEVANCE\s*[:=]\s*(\d)", response_text)
        if not relevance_match:
            raise ValueError(
                f"Could not parse relevance score from LLM response. "
                f"Expected 'RELEVANCE: <0-3>'. Got:\n{response_text}"
            )
        relevance = int(relevance_match.group(1))
        if relevance not in (0, 1, 2, 3):
            raise ValueError(
                f"Relevance score must be 0, 1, 2, or 3. "
                f"Got: {relevance}. Response:\n{response_text}"
            )

        # Extract diversity score
        diversity_match = re.search(r"(?i)DIVERSITY\s*[:=]\s*(\d)", response_text)
        if not diversity_match:
            raise ValueError(
                f"Could not parse diversity score from LLM response. "
                f"Expected 'DIVERSITY: <0-3>'. Got:\n{response_text}"
            )
        diversity = int(diversity_match.group(1))
        if diversity not in (0, 1, 2, 3):
            raise ValueError(
                f"Diversity score must be 0, 1, 2, or 3. "
                f"Got: {diversity}. Response:\n{response_text}"
            )

        # Extract flagged suggestions
        flagged_match = re.search(r"(?i)FLAGGED\s*[:=]\s*(.*?)(?:\n|$)", response_text)
        flagged: list[str] = []
        if flagged_match:
            raw = flagged_match.group(1).strip()
            if raw.lower() != "none" and raw:
                flagged = [s.strip() for s in raw.split(",") if s.strip()]

        # Extract reasoning
        reasoning_match = re.search(r"(?is)REASONING\s*[:=]\s*(.*)", response_text)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return relevance, diversity, flagged, reasoning
