"""Tests for core data types."""

from veritail.types import (
    CheckResult,
    ExperimentConfig,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResult,
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
    assert result.image_url is None
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
        image_url="https://example.com/img.jpg",
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
    assert entry.frequency is None


def test_query_entry_full():
    entry = QueryEntry(
        query="running shoes",
        type="broad",
        category="Shoes > Running",
        frequency=1500,
    )
    assert entry.query == "running shoes"
    assert entry.type == "broad"
    assert entry.frequency == 1500


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
    assert judgment.metadata == {}


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
        rubric="ecommerce-default",
    )
    assert config.top_k == 10


def test_metric_result_defaults():
    metric = MetricResult(metric_name="ndcg@10", value=0.85)
    assert metric.per_query == {}
    assert metric.by_query_type == {}
