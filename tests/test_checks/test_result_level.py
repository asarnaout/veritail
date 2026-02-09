"""Tests for result-level deterministic checks."""

from search_eval.checks.result_level import (
    check_attribute_match,
    check_category_alignment,
    check_duplicates,
    check_price_outliers,
    check_text_overlap,
)
from search_eval.types import QueryEntry, SearchResult


def _make_result(
    product_id: str = "SKU-001",
    title: str = "Test Product",
    category: str = "Test",
    price: float = 9.99,
    position: int = 0,
    attributes: dict = None,
) -> SearchResult:
    return SearchResult(
        product_id=product_id,
        title=title,
        description="Test description",
        category=category,
        price=price,
        position=position,
        attributes=attributes or {},
    )


class TestCategoryAlignment:
    def test_matching_expected_category(self):
        query = QueryEntry(query="running shoes", category="Shoes > Running")
        results = [_make_result(category="Shoes > Running")]
        checks = check_category_alignment(query, results)
        assert len(checks) == 1
        assert checks[0].passed

    def test_mismatching_expected_category(self):
        query = QueryEntry(query="running shoes", category="Shoes > Running")
        results = [_make_result(category="Electronics > Headphones")]
        checks = check_category_alignment(query, results)
        assert len(checks) == 1
        assert not checks[0].passed

    def test_majority_category_no_expected(self):
        query = QueryEntry(query="running shoes")
        results = [
            _make_result("SKU-1", category="Shoes > Running"),
            _make_result("SKU-2", category="Shoes > Casual"),
            _make_result("SKU-3", category="Electronics > Headphones"),
        ]
        checks = check_category_alignment(query, results)
        # 2 shoes, 1 electronics -> shoes is majority
        shoes_checks = [c for c in checks if c.passed]
        mismatched = [c for c in checks if not c.passed]
        assert len(shoes_checks) == 2
        assert len(mismatched) == 1

    def test_empty_results(self):
        query = QueryEntry(query="running shoes", category="Shoes")
        checks = check_category_alignment(query, [])
        assert len(checks) == 0


class TestAttributeMatch:
    def test_color_match(self):
        results = [_make_result(attributes={"color": "red"})]
        checks = check_attribute_match("red dress", results)
        assert len(checks) == 1
        assert checks[0].passed

    def test_color_mismatch(self):
        results = [_make_result(attributes={"color": "blue"})]
        checks = check_attribute_match("red dress", results)
        assert len(checks) == 1
        assert not checks[0].passed

    def test_no_color_in_query(self):
        results = [_make_result(attributes={"color": "red"})]
        checks = check_attribute_match("running shoes", results)
        assert len(checks) == 0

    def test_no_attributes_on_result(self):
        results = [_make_result()]
        checks = check_attribute_match("red dress", results)
        assert len(checks) == 1
        assert not checks[0].passed


class TestTextOverlap:
    def test_high_overlap(self):
        results = [_make_result(title="Running Shoes Nike")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert checks[0].passed

    def test_no_overlap(self):
        results = [_make_result(title="Kitchen Blender Pro")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert not checks[0].passed
        assert checks[0].severity == "fail"

    def test_partial_overlap(self):
        results = [_make_result(title="Nike Running Jacket Waterproof")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        # "running" overlaps -> should pass with default threshold of 0.1
        assert checks[0].passed


class TestPriceOutliers:
    def test_no_outliers(self):
        results = [
            _make_result(f"SKU-{i}", price=p)
            for i, p in enumerate([100, 110, 120, 130, 140])
        ]
        checks = check_price_outliers("shoes", results)
        assert all(c.passed for c in checks)

    def test_high_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p)
            for i, p in enumerate([100, 110, 120, 130, 999])
        ]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("999" in c.detail for c in outliers)

    def test_too_few_results(self):
        results = [_make_result("SKU-1", price=10), _make_result("SKU-2", price=20)]
        checks = check_price_outliers("shoes", results)
        assert len(checks) == 0  # Need at least 3 for IQR


class TestDuplicates:
    def test_near_duplicates_detected(self):
        results = [
            _make_result("SKU-1", title="Nike Air Max 90 Running Shoes Black"),
            _make_result("SKU-2", title="Nike Air Max 90 Running Shoes White"),
        ]
        checks = check_duplicates("shoes", results)
        # These titles are very similar
        assert len(checks) == 1
        assert not checks[0].passed
        assert checks[0].check_name == "duplicate"

    def test_no_duplicates(self):
        results = [
            _make_result("SKU-1", title="Nike Air Max 90 Running Shoes"),
            _make_result("SKU-2", title="Kitchen Blender Professional Grade"),
        ]
        checks = check_duplicates("shoes", results)
        assert len(checks) == 0

    def test_single_result(self):
        results = [_make_result("SKU-1", title="Test Product")]
        checks = check_duplicates("shoes", results)
        assert len(checks) == 0
