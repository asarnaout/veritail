"""Tests for result-level deterministic checks."""

from veritail.checks.result_level import (
    check_duplicates,
    check_out_of_stock_prominence,
    check_price_outliers,
    check_text_overlap,
    check_title_length,
)
from veritail.types import SearchResult


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
        results = [
            _make_result(
                title="Modern Leather Sofa Set",
                category="Living Room Seating Shoes",
            )
        ]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert checks[0].passed
        assert "category" in checks[0].detail

    def test_description_match_saves_title_miss(self):
        results = [
            _make_result(
                title="Premium Sofa Set",
                description="Great for running outdoors",
            )
        ]
        checks = check_text_overlap("running shoes", results)
        assert len(checks) == 1
        assert checks[0].passed
        assert "description" in checks[0].detail

    def test_empty_fields_no_penalty(self):
        results = [
            _make_result(
                title="Running Shoes Nike",
                description="",
                category="",
            )
        ]
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
        assert len(checks) == 0  # Need at least 3

    # --- MAD path (n=3-7) ---

    def test_mad_3_items_obvious_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p) for i, p in enumerate([20, 20, 5000])
        ]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) == 1
        assert "5000" in outliers[0].detail

    def test_mad_3_items_low_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p) for i, p in enumerate([1, 500, 500])
        ]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) == 1
        assert "1.00" in outliers[0].detail

    def test_mad_3_items_no_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p) for i, p in enumerate([20, 22, 25])
        ]
        checks = check_price_outliers("shoes", results)
        assert all(c.passed for c in checks)

    def test_mad_5_items_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p)
            for i, p in enumerate([10, 12, 11, 13, 500])
        ]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("500" in c.detail for c in outliers)

    def test_mad_7_items_outlier(self):
        results = [
            _make_result(f"SKU-{i}", price=p)
            for i, p in enumerate([50, 52, 48, 51, 49, 53, 900])
        ]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("900" in c.detail for c in outliers)

    def test_mad_all_same_price(self):
        results = [_make_result(f"SKU-{i}", price=20) for i in range(3)]
        checks = check_price_outliers("shoes", results)
        assert all(c.passed for c in checks)

    # --- IQR path (n>=8) ---

    def test_iqr_8_items_outlier(self):
        prices = [100, 102, 98, 105, 101, 99, 103, 999]
        results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("999" in c.detail for c in outliers)

    def test_iqr_8_items_no_outlier(self):
        prices = [100, 102, 98, 105, 101, 99, 103, 104]
        results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
        checks = check_price_outliers("shoes", results)
        assert all(c.passed for c in checks)

    def test_iqr_interpolated_quartiles(self):
        """Verify interpolation works — the old naive method would not flag this."""
        # 9 items: old method Q1=sorted[2], Q3=sorted[6]
        # With interpolation, quartiles are more precise
        prices = [10, 20, 30, 40, 50, 60, 70, 80, 300]
        results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("300" in c.detail for c in outliers)

    # --- Boundary tests ---

    def test_boundary_n7_uses_mad(self):
        """7 items — MAD path should detect outlier that old IQR would miss."""
        prices = [20, 21, 22, 23, 24, 25, 500]
        results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("500" in c.detail for c in outliers)

    def test_boundary_n8_uses_iqr(self):
        """8 items — IQR path should work correctly."""
        prices = [20, 21, 22, 23, 24, 25, 26, 500]
        results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
        checks = check_price_outliers("shoes", results)
        outliers = [c for c in checks if not c.passed]
        assert len(outliers) >= 1
        assert any("500" in c.detail for c in outliers)

    # --- False-positive regression tests ---

    def test_mad_no_false_positive_small_diff(self):
        """Normal price variation among identical items must not be flagged."""
        for prices in [
            [20, 20, 25],  # 25% diff
            [20, 20, 40],  # 2x diff
            [100, 100, 150],  # 50% diff
            [100, 100, 100, 100, 200],  # n=5, 2x
        ]:
            results = [_make_result(f"SKU-{i}", price=p) for i, p in enumerate(prices)]
            checks = check_price_outliers("shoes", results)
            outliers = [c for c in checks if not c.passed]
            assert outliers == [], (
                f"False positive in {prices}: {[c.detail for c in outliers]}"
            )


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
