"""Tests for result-level deterministic checks."""

from veritail.checks.result_level import (
    check_category_alignment,
    check_duplicates,
    check_out_of_stock_prominence,
    check_price_outliers,
    check_text_overlap,
    check_title_length,
)
from veritail.types import QueryEntry, SearchResult


def _make_result(
    product_id: str = "SKU-001",
    title: str = "Test Product",
    description: str = "Test description",
    category: str = "Test",
    price: float = 9.99,
    position: int = 0,
    attributes: dict = None,
) -> SearchResult:
    return SearchResult(
        product_id=product_id,
        title=title,
        description=description,
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
        assert checks[0].severity == "warning"

    def test_partial_overlap(self):
        results = [_make_result(title="Nike Running Jacket Waterproof")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        # "running" overlaps -> should pass with default threshold of 0.1
        assert checks[0].passed

    def test_category_match_saves_title_miss(self):
        results = [_make_result(title="Modern Leather Sofa Set", category="Living Room Seating Shoes")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert checks[0].passed
        assert "category" in checks[0].detail

    def test_description_match_saves_title_miss(self):
        results = [_make_result(title="Premium Sofa Set", description="Great for running outdoors")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert checks[0].passed
        assert "description" in checks[0].detail

    def test_empty_fields_no_penalty(self):
        results = [_make_result(title="Running Shoes Nike", description="", category="")]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
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


class TestTitleLength:
    def test_normal_title(self):
        results = [_make_result(title="Nike Air Max 90 Running Shoes")]
        checks = check_title_length("shoes", results)
        assert len(checks) == 1
        assert checks[0].passed
        assert checks[0].check_name == "title_length"
        assert checks[0].severity == "info"

    def test_long_title_seo_stuffing(self):
        long_title = "Nike Air Max 90 Running Shoes " * 5  # ~150 chars
        results = [_make_result(title=long_title)]
        checks = check_title_length("shoes", results)
        assert len(checks) == 1
        assert not checks[0].passed
        assert checks[0].severity == "info"
        assert ">" in checks[0].detail

    def test_short_title_malformed(self):
        results = [_make_result(title="SKU-123")]
        checks = check_title_length("shoes", results)
        assert len(checks) == 1
        assert not checks[0].passed
        assert checks[0].severity == "info"
        assert "<" in checks[0].detail

    def test_exactly_at_boundaries(self):
        results = [
            _make_result("SKU-1", title="A" * 10),
            _make_result("SKU-2", title="B" * 120),
        ]
        checks = check_title_length("shoes", results)
        assert len(checks) == 2
        assert all(c.passed for c in checks)

    def test_custom_thresholds(self):
        results = [_make_result(title="A" * 50)]
        checks = check_title_length("shoes", results, max_length=40, min_length=20)
        assert len(checks) == 1
        assert not checks[0].passed
        assert "> 40" in checks[0].detail


class TestOutOfStockProminence:
    def test_position_1_out_of_stock_is_fail(self):
        results = [_make_result("SKU-1", title="Product A", position=0)]
        results[0].in_stock = False

        checks = check_out_of_stock_prominence("shoes", results)

        assert len(checks) == 1
        assert checks[0].check_name == "out_of_stock_prominence"
        assert not checks[0].passed
        assert checks[0].severity == "fail"

    def test_positions_2_to_5_out_of_stock_are_warning(self):
        results = [
            _make_result(f"SKU-{i}", title=f"Product {i}", position=i)
            for i in range(1, 5)
        ]
        for result in results:
            result.in_stock = False

        checks = check_out_of_stock_prominence("shoes", results)

        assert len(checks) == 4
        assert all(not c.passed for c in checks)
        assert all(c.severity == "warning" for c in checks)

    def test_out_of_stock_below_top_5_passes(self):
        results = [_make_result("SKU-7", title="Product 7", position=6)]
        results[0].in_stock = False

        checks = check_out_of_stock_prominence("shoes", results)

        assert len(checks) == 1
        assert checks[0].passed
        assert checks[0].severity == "info"

    def test_in_stock_passes(self):
        results = [_make_result("SKU-1", title="Product A", position=0)]
        results[0].in_stock = True

        checks = check_out_of_stock_prominence("shoes", results)

        assert len(checks) == 1
        assert checks[0].passed
        assert checks[0].severity == "info"
