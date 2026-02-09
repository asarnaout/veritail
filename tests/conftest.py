"""Shared test fixtures for veritail."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.types import (
    CheckResult,
    HumanScore,
    JudgmentRecord,
    QueryEntry,
    SearchResult,
)


@pytest.fixture
def sample_search_result() -> SearchResult:
    return SearchResult(
        product_id="SKU-001",
        title="Nike Air Max 90 Running Shoes",
        description="Classic running shoes with Air Max cushioning",
        category="Shoes > Running",
        price=129.99,
        position=0,
        attributes={"color": "black", "brand": "Nike", "size": "10"},
        in_stock=True,
    )


@pytest.fixture
def sample_search_results() -> list[SearchResult]:
    return [
        SearchResult(
            product_id="SKU-001",
            title="Nike Air Max 90 Running Shoes",
            description="Classic running shoes",
            category="Shoes > Running",
            price=129.99,
            position=0,
            attributes={"color": "black", "brand": "Nike"},
            in_stock=True,
        ),
        SearchResult(
            product_id="SKU-002",
            title="Adidas Ultraboost Running Shoes",
            description="Premium running shoes with Boost technology",
            category="Shoes > Running",
            price=179.99,
            position=1,
            attributes={"color": "white", "brand": "Adidas"},
            in_stock=True,
        ),
        SearchResult(
            product_id="SKU-003",
            title="New Balance 990v5 Running Shoes",
            description="Made in USA premium running shoes",
            category="Shoes > Running",
            price=184.99,
            position=2,
            attributes={"color": "grey", "brand": "New Balance"},
            in_stock=True,
        ),
    ]


@pytest.fixture
def sample_query_entry() -> QueryEntry:
    return QueryEntry(
        query="running shoes",
        type="broad",
        category="Shoes > Running",
    )


@pytest.fixture
def sample_judgment(sample_search_result: SearchResult) -> JudgmentRecord:
    return JudgmentRecord(
        query="running shoes",
        product=sample_search_result,
        score=3,
        reasoning="Exact match for running shoes query.",
        model="claude-sonnet-4-5",
        experiment="test-experiment",
    )


@pytest.fixture
def sample_human_score() -> HumanScore:
    return HumanScore(
        query="running shoes",
        product_id="SKU-001",
        score=3,
        experiment="test-experiment",
    )


@pytest.fixture
def sample_check_result() -> CheckResult:
    return CheckResult(
        check_name="category_alignment",
        query="running shoes",
        product_id="SKU-001",
        passed=True,
        detail="Product is in expected category",
        severity="info",
    )
