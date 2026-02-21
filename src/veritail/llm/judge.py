"""LLM-based relevance judgment for query-result pairs."""

from __future__ import annotations

import re
from collections.abc import Callable

from veritail.llm.client import BatchRequest, LLMClient, LLMResponse
from veritail.types import CorrectionJudgment, JudgmentRecord, SearchResult

CORRECTION_SYSTEM_PROMPT = """\
You are an expert ecommerce search quality analyst. Your task is to judge whether \
a search engine's query correction (autocorrect / "did you mean") was appropriate.

## Criteria

A correction is **appropriate** when:
- It fixes a clear spelling mistake (e.g. "runnign shoes" -> "running shoes")
- It normalizes common typos or transpositions
- The corrected query preserves the shopper's original intent

A correction is **inappropriate** when:
- It changes the shopper's intent (e.g. "plats" -> "planes" in a foodservice context \
where "plats" means plates)
- It corrects away a valid brand name, model number, or industry jargon \
(e.g. "Cambro" -> "Camaro")
- The original query is a valid catalog term that the search engine should recognize

## Response Format

You MUST respond in exactly this format:

VERDICT: <verdict>
REASONING: <your concise justification in 1-2 sentences>

Where <verdict> is exactly one of: appropriate, inappropriate
"""


class RelevanceJudge:
    """Judges the relevance of search results to queries using an LLM."""

    def __init__(
        self,
        client: LLMClient,
        system_prompt: str,
        format_user_prompt: Callable[..., str],
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
        corrected_query: str | None = None,
        overlay: str | None = None,
    ) -> JudgmentRecord:
        """Judge the relevance of a single search result to a query."""
        kwargs: dict[str, str] = {}
        if corrected_query is not None:
            kwargs["corrected_query"] = corrected_query
        if overlay is not None:
            kwargs["overlay"] = overlay
        if kwargs:
            try:
                user_prompt = self._format_user_prompt(query, result, **kwargs)
            except TypeError:
                user_prompt = self._format_user_prompt(query, result)
        else:
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

    def prepare_request(
        self,
        custom_id: str,
        query: str,
        result: SearchResult,
        *,
        corrected_query: str | None = None,
        overlay: str | None = None,
    ) -> BatchRequest:
        """Build a BatchRequest for a single query-result pair."""
        kwargs: dict[str, str] = {}
        if corrected_query is not None:
            kwargs["corrected_query"] = corrected_query
        if overlay is not None:
            kwargs["overlay"] = overlay
        if kwargs:
            try:
                user_prompt = self._format_user_prompt(query, result, **kwargs)
            except TypeError:
                user_prompt = self._format_user_prompt(query, result)
        else:
            user_prompt = self._format_user_prompt(query, result)
        return BatchRequest(
            custom_id=custom_id,
            system_prompt=self._system_prompt,
            user_prompt=user_prompt,
        )

    def parse_batch_result(
        self,
        response: LLMResponse,
        query: str,
        result: SearchResult,
        *,
        query_type: str | None = None,
    ) -> JudgmentRecord:
        """Parse a batch response into a JudgmentRecord."""
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
    def _parse_response(response_text: str) -> tuple[int, str, str]:
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
                f"Score must be 0, 1, 2, or 3. Got: {score}. Response:\n{response_text}"
            )

        # Extract attribute verdict (default to "n/a" for custom rubrics)
        attr_match = re.search(
            r"(?i)ATTRIBUTES\s*[:=]\s*(\w[\w/ ]*?)(?:\n|$)",
            response_text,
        )
        attribute_verdict = attr_match.group(1).strip().lower() if attr_match else "n/a"

        # Extract reasoning
        reasoning_match = re.search(
            r"(?is)REASONING\s*[:=]\s*(.*)",
            response_text,
        )
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return score, attribute_verdict, reasoning


class CorrectionJudge:
    """Judges whether a query correction was appropriate using an LLM."""

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
        original_query: str,
        corrected_query: str,
    ) -> CorrectionJudgment:
        """Judge whether a query correction was appropriate."""
        user_prompt = self._format_user_prompt(original_query, corrected_query)
        response = self._client.complete(self._system_prompt, user_prompt)

        verdict, reasoning = self._parse_response(response.content)

        return CorrectionJudgment(
            original_query=original_query,
            corrected_query=corrected_query,
            verdict=verdict,
            reasoning=reasoning,
            model=response.model,
            experiment=self._experiment,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )

    def prepare_request(
        self, custom_id: str, original_query: str, corrected_query: str
    ) -> BatchRequest:
        """Build a BatchRequest for a correction judgment."""
        user_prompt = self._format_user_prompt(original_query, corrected_query)
        return BatchRequest(
            custom_id=custom_id,
            system_prompt=self._system_prompt,
            user_prompt=user_prompt,
        )

    def parse_batch_result(
        self, response: LLMResponse, original_query: str, corrected_query: str
    ) -> CorrectionJudgment:
        """Parse a batch response into a CorrectionJudgment."""
        verdict, reasoning = self._parse_response(response.content)
        return CorrectionJudgment(
            original_query=original_query,
            corrected_query=corrected_query,
            verdict=verdict,
            reasoning=reasoning,
            model=response.model,
            experiment=self._experiment,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
            },
        )

    @staticmethod
    def _format_user_prompt(original: str, corrected: str) -> str:
        return (
            f"## Original Query\n{original}\n\n"
            f"## Corrected Query\n{corrected}\n\n"
            "Was this correction appropriate?"
        )

    @staticmethod
    def _parse_response(response_text: str) -> tuple[str, str]:
        """Parse verdict and reasoning from LLM response."""
        verdict_match = re.search(
            r"(?i)VERDICT\s*[:=]\s*(appropriate|inappropriate)",
            response_text,
        )
        verdict = verdict_match.group(1).lower() if verdict_match else "error"

        reasoning_match = re.search(
            r"(?is)REASONING\s*[:=]\s*(.*)",
            response_text,
        )
        reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

        return verdict, reasoning
