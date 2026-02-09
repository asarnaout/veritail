"""Tests for FileBackend."""

from __future__ import annotations

import csv

from veritail.backends.file import FileBackend
from veritail.types import JudgmentRecord, SearchResult


def _make_judgment(
    query: str = "running shoes",
    product_id: str = "SKU-001",
    score: int = 3,
    experiment: str = "test-exp",
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

    def test_get_human_scores(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))

        # Create the experiment directory and human scores file
        exp_dir = tmp_path / "test-exp"
        exp_dir.mkdir()
        scores_file = exp_dir / "human-scores.csv"
        with open(scores_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["query", "product_id", "human_score"])
            writer.writerow(["running shoes", "SKU-001", "3"])
            writer.writerow(["running shoes", "SKU-002", "2"])
            writer.writerow(["laptop", "SKU-003", ""])  # blank = skip

        scores = backend.get_human_scores("test-exp")
        assert len(scores) == 2
        assert scores[0].query == "running shoes"
        assert scores[0].product_id == "SKU-001"
        assert scores[0].score == 3

    def test_get_human_scores_empty(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))
        scores = backend.get_human_scores("nonexistent")
        assert scores == []

    def test_create_review_queue_random(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))

        # Log 10 judgments
        for i in range(10):
            backend.log_judgment(_make_judgment(product_id=f"SKU-{i:03d}", score=i % 4))

        backend.create_review_queue("test-exp", sample_rate=0.5, strategy="random")

        review_file = tmp_path / "test-exp" / "review-sample.csv"
        assert review_file.exists()

        with open(review_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 5  # 50% of 10
            assert rows[0]["human_score"] == ""  # blank for reviewer
            assert "query" in reader.fieldnames
            assert "llm_score" in reader.fieldnames

    def test_create_review_queue_stratified(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))

        # Log judgments with different scores
        for i in range(12):
            backend.log_judgment(_make_judgment(product_id=f"SKU-{i:03d}", score=i % 4))

        backend.create_review_queue("test-exp", sample_rate=0.5, strategy="stratified")

        review_file = tmp_path / "test-exp" / "review-sample.csv"
        assert review_file.exists()

    def test_create_review_queue_empty(self, tmp_path):
        backend = FileBackend(output_dir=str(tmp_path))
        backend.create_review_queue("test-exp", sample_rate=0.5)
        # Should not create file if no judgments
        review_file = tmp_path / "test-exp" / "review-sample.csv"
        assert not review_file.exists()

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
            ),
            score=3,
            reasoning="Perfect color match",
            model="test-model",
            experiment="test-exp",
            metadata={"input_tokens": 100},
        )
        backend.log_judgment(judgment)

        loaded = backend.get_judgments("test-exp")
        assert len(loaded) == 1
        assert loaded[0].product.attributes == {"color": "red", "brand": "Nike"}
        assert loaded[0].product.image_url == "https://example.com/img.jpg"
        assert loaded[0].metadata == {"input_tokens": 100}
