"""Inter-rater agreement computation (Cohen's kappa)."""

from __future__ import annotations

from search_eval.types import HumanScore, JudgmentRecord


def cohens_kappa(ratings_a: list[int], ratings_b: list[int]) -> float:
    """Compute Cohen's kappa for two sets of ordinal ratings.

    Args:
        ratings_a: First rater's scores (e.g., LLM scores)
        ratings_b: Second rater's scores (e.g., human scores)

    Returns:
        Kappa value in [-1, 1]. 1 = perfect agreement, 0 = chance agreement.
    """
    if len(ratings_a) != len(ratings_b):
        raise ValueError("Rating lists must be the same length")
    if not ratings_a:
        return 0.0

    n = len(ratings_a)

    # All unique categories from both raters
    categories = sorted(set(ratings_a) | set(ratings_b))

    # Build confusion matrix counts
    # p_o = observed agreement
    agreements = sum(1 for a, b in zip(ratings_a, ratings_b) if a == b)
    p_o = agreements / n

    # p_e = expected agreement by chance
    p_e = 0.0
    for cat in categories:
        count_a = sum(1 for r in ratings_a if r == cat)
        count_b = sum(1 for r in ratings_b if r == cat)
        p_e += (count_a / n) * (count_b / n)

    if p_e == 1.0:
        return 1.0  # Both raters always agree on the same category

    return (p_o - p_e) / (1 - p_e)


def compute_agreement(
    judgments: list[JudgmentRecord],
    human_scores: list[HumanScore],
) -> dict:
    """Compute inter-rater agreement between LLM and human judgments.

    Matches judgments to human scores by (query, product_id) pairs.

    Returns:
        Dict with keys:
        - kappa: Cohen's kappa value
        - n_matched: Number of matched pairs
        - agreement_rate: Exact match percentage
        - calibration: Decision string based on kappa thresholds
    """
    # Build lookup: (query, product_id) -> llm_score
    llm_lookup: dict[tuple[str, str], int] = {}
    for j in judgments:
        key = (j.query, j.product.product_id)
        llm_lookup[key] = j.score

    # Match human scores to LLM scores
    llm_scores: list[int] = []
    human_score_list: list[int] = []

    for hs in human_scores:
        key = (hs.query, hs.product_id)
        if key in llm_lookup:
            llm_scores.append(llm_lookup[key])
            human_score_list.append(hs.score)

    n_matched = len(llm_scores)

    if n_matched == 0:
        return {
            "kappa": 0.0,
            "n_matched": 0,
            "agreement_rate": 0.0,
            "calibration": "No matched pairs found for agreement computation",
        }

    kappa = cohens_kappa(llm_scores, human_score_list)
    exact_matches = sum(1 for a, b in zip(llm_scores, human_score_list) if a == b)
    agreement_rate = exact_matches / n_matched

    if kappa > 0.7:
        calibration = "LLM judgments are trustworthy (kappa > 0.7)"
    elif kappa > 0.4:
        calibration = "LLM has systematic biases — review rubric prompts and re-run (kappa 0.4-0.7)"
    else:
        calibration = "LLM judgments are unreliable — expand human review or fix rubrics (kappa < 0.4)"

    return {
        "kappa": kappa,
        "n_matched": n_matched,
        "agreement_rate": agreement_rate,
        "calibration": calibration,
    }
