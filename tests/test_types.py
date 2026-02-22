"""Tests for core data types."""

from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    ExperimentConfig,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResponse,
    SearchResult,
    VerticalContext,
    VerticalOverlay,
)


def test_search_result_defaults():
    result = SearchResult(
        product_id="SKU-001",
        title="Test Product",
        description="A test product",
        category="Test",
        price=9.99,
        position=0,
    )
    assert result.attributes == {}
    assert result.in_stock is True
    assert result.metadata == {}


def test_search_result_full():
    result = SearchResult(
        product_id="SKU-001",
        title="Test Product",
        description="A test product",
        category="Test > Sub",
        price=9.99,
        position=0,
        attributes={"color": "red"},
        in_stock=False,
        metadata={"highlights": ["On sale"], "source": "api-v2"},
    )
    assert result.product_id == "SKU-001"
    assert result.attributes["color"] == "red"
    assert result.in_stock is False
    assert result.metadata == {"highlights": ["On sale"], "source": "api-v2"}


def test_query_entry_defaults():
    entry = QueryEntry(query="running shoes")
    assert entry.type is None
    assert entry.category is None
    assert entry.overlay is None


def test_query_entry_full():
    entry = QueryEntry(
        query="running shoes",
        type="broad",
        category="Shoes > Running",
    )
    assert entry.query == "running shoes"
    assert entry.type == "broad"
    assert entry.category == "Shoes > Running"


def test_query_entry_with_overlay():
    entry = QueryEntry(
        query="commercial fryer",
        type="broad",
        overlay="hot_side",
    )
    assert entry.overlay == "hot_side"


def test_judgment_record(sample_search_result):
    judgment = JudgmentRecord(
        query="running shoes",
        product=sample_search_result,
        score=2,
        reasoning="Good match",
        model="test-model",
        experiment="exp-1",
    )
    assert judgment.score == 2
    assert judgment.query_type is None
    assert judgment.metadata == {}


def test_judgment_record_with_query_type(sample_search_result):
    judgment = JudgmentRecord(
        query="running shoes",
        product=sample_search_result,
        score=2,
        reasoning="Good match",
        model="test-model",
        experiment="exp-1",
        query_type="broad",
    )
    assert judgment.query_type == "broad"


def test_check_result_defaults():
    check = CheckResult(
        check_name="test_check",
        query="running shoes",
        product_id=None,
        passed=True,
        detail="All good",
    )
    assert check.severity == "warning"


def test_experiment_config_defaults():
    config = ExperimentConfig(
        name="test",
        adapter_path="adapter.py",
        llm_model="claude-sonnet-4-5",
    )
    assert config.top_k == 10


def test_metric_result_defaults():
    metric = MetricResult(metric_name="ndcg@10", value=0.85)
    assert metric.per_query == {}
    assert metric.by_query_type == {}


def test_search_response_defaults():
    result = SearchResult(
        product_id="SKU-001",
        title="Test",
        description="Desc",
        category="Cat",
        price=9.99,
        position=0,
    )
    response = SearchResponse(results=[result])
    assert response.corrected_query is None
    assert len(response.results) == 1


def test_search_response_with_correction():
    response = SearchResponse(results=[], corrected_query="plates")
    assert response.corrected_query == "plates"
    assert response.results == []


def test_correction_judgment_defaults():
    cj = CorrectionJudgment(
        original_query="plats",
        corrected_query="plates",
        verdict="appropriate",
        reasoning="Spelling fix",
        model="test-model",
        experiment="exp-1",
    )
    assert cj.metadata == {}
    assert cj.verdict == "appropriate"


def test_correction_judgment_with_metadata():
    cj = CorrectionJudgment(
        original_query="plats",
        corrected_query="plates",
        verdict="inappropriate",
        reasoning="Valid term",
        model="test-model",
        experiment="exp-1",
        metadata={"input_tokens": 100},
    )
    assert cj.metadata["input_tokens"] == 100


def test_vertical_overlay_construction():
    overlay = VerticalOverlay(
        description="Hot-side cooking equipment",
        content="Ovens, fryers, griddles, salamanders.",
    )
    assert overlay.description == "Hot-side cooking equipment"
    assert "fryers" in overlay.content


def test_vertical_context_defaults():
    ctx = VerticalContext(core="## Vertical: Test\nSome guidance.")
    assert ctx.core == "## Vertical: Test\nSome guidance."
    assert ctx.overlays == {}


def test_vertical_context_with_overlays():
    ctx = VerticalContext(
        core="## Vertical: Foodservice\nCore guidance.",
        overlays={
            "hot_side": VerticalOverlay(
                description="Hot-side equipment",
                content="Ovens and fryers.",
            ),
            "cold_side": VerticalOverlay(
                description="Refrigeration",
                content="Reach-ins and undercounters.",
            ),
        },
    )
    assert len(ctx.overlays) == 2
    assert "hot_side" in ctx.overlays
    assert ctx.overlays["cold_side"].description == "Refrigeration"
