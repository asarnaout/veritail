"""Tests for FileBackend."""

from __future__ import annotations

from veritail.backends.file import FileBackend
from veritail.types import JudgmentRecord, SearchResult


def _make_judgment(
    query: str = "running shoes",
    product_id: str = "SKU-001",
    score: int = 3,
    experiment: str = "test-exp",
    attribute_verdict: str = "match",
) -> JudgmentRecord:
    return JudgmentRecord(
        query=query,
        product=SearchResult(
            product_id=product_id,
            title="Nike Running Shoes",
            description="Classic running shoes",
            category="Shoes > Running",
            price=129.99,
            position=0,
            attributes={"color": "black"},
        ),
        score=score,
        reasoning="Good match",
        attribute_verdict=attribute_verdict,
        model="test-model",
        experiment=experiment,
    )


class TestFileBackend:
    def test_log_and_get_judgments(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))

        j1 = _make_judgment(product_id="SKU-001", score=3)
        j2 = _make_judgment(product_id="SKU-002", score=1)
        backend.log_judgment(j1)
        backend.log_judgment(j2)

        judgments = backend.get_judgments("test-exp")
        assert len(judgments) == 2
        assert judgments[0].product.product_id == "SKU-001"
        assert judgments[0].score == 3
        assert judgments[1].product.product_id == "SKU-002"
        assert judgments[1].score == 1

    def test_log_experiment(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))
        backend.log_experiment("test-exp", {"llm_model": "claude-sonnet-4-5", "top_k": 10})

        config_file = tmp_path / "test-exp" / "config.json"
        assert config_file.exists()

    def test_get_judgments_empty(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))
        judgments = backend.get_judgments("nonexistent")
        assert judgments == []

    def test_round_trip_with_attributes(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))

        judgment = JudgmentRecord(
            query="red shoes",
            product=SearchResult(
                product_id="SKU-X",
                title="Red Nike Shoes",
                description="Bright red",
                category="Shoes",
                price=99.99,
                position=2,
                attributes={"color": "red", "brand": "Nike"},
                in_stock=True,
                image_url="https://example.com/img.jpg",
                metadata={"highlights": ["Free shipping"]},
            ),
            score=3,
            reasoning="Perfect color match",
            attribute_verdict="match",
            model="test-model",
            experiment="test-exp",
            query_type="attribute",
            metadata={"input_tokens": 100},
        )
        backend.log_judgment(judgment)

        loaded = backend.get_judgments("test-exp")
        assert len(loaded) == 1
        assert loaded[0].product.attributes == {"color": "red", "brand": "Nike"}
        assert loaded[0].product.image_url == "https://example.com/img.jpg"
        assert loaded[0].product.metadata == {"highlights": ["Free shipping"]}
        assert loaded[0].attribute_verdict == "match"
        assert loaded[0].query_type == "attribute"
        assert loaded[0].metadata == {"input_tokens": 100}

    def test_backwards_compat_missing_attribute_verdict(self, tmp_path):
        """Old JSONL files without attribute_verdict should load with default 'n/a'."""
        backend = FileBackend(output_dir=str(tmp_path))
        exp_dir = tmp_path / "test-exp"
        exp_dir.mkdir(parents=True, exist_ok=True)

        # Write a JSONL line without attribute_verdict (simulates old data)
        import json
        old_record = {
            "query": "shoes",
            "product": {
                "product_id": "SKU-OLD",
                "title": "Old Shoes",
                "description": "From before attribute_verdict existed",
                "category": "Shoes",
                "price": 50.0,
                "position": 0,
            },
            "score": 2,
            "reasoning": "Decent match",
            "model": "old-model",
            "experiment": "test-exp",
            "metadata": {},
        }
        with open(exp_dir / "judgments.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps(old_record) + "\n")

        loaded = backend.get_judgments("test-exp")
        assert len(loaded) == 1
        assert loaded[0].attribute_verdict == "n/a"
