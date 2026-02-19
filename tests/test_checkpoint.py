"""Tests for checkpoint filename parameter."""

from __future__ import annotations

from veritail.checkpoint import (
    BatchCheckpoint,
    clear_checkpoint,
    load_checkpoint,
    save_checkpoint,
)


def _make_checkpoint(name: str = "exp") -> BatchCheckpoint:
    return BatchCheckpoint(
        batch_id="batch-1",
        experiment_name=name,
        phase="relevance",
        request_context={},
        checks=[],
        correction_entries=[],
    )


class TestCheckpointFilename:
    def test_save_load_default_filename(self, tmp_path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(str(tmp_path), "exp", cp)
        loaded = load_checkpoint(str(tmp_path), "exp")
        assert loaded is not None
        assert loaded.batch_id == "batch-1"
        assert (tmp_path / "exp" / "checkpoint.json").exists()

    def test_save_load_custom_filename(self, tmp_path) -> None:
        cp = _make_checkpoint()
        save_checkpoint(str(tmp_path), "exp", cp, filename="ac-checkpoint.json")
        # Default filename should not exist
        assert not (tmp_path / "exp" / "checkpoint.json").exists()
        # Custom filename should exist
        assert (tmp_path / "exp" / "ac-checkpoint.json").exists()
        loaded = load_checkpoint(str(tmp_path), "exp", filename="ac-checkpoint.json")
        assert loaded is not None
        assert loaded.batch_id == "batch-1"
        # Loading with default filename returns None
        assert load_checkpoint(str(tmp_path), "exp") is None

    def test_clear_custom_filename(self, tmp_path) -> None:
        cp_default = _make_checkpoint()
        cp_custom = _make_checkpoint()
        cp_custom.batch_id = "batch-2"
        save_checkpoint(str(tmp_path), "exp", cp_default)
        save_checkpoint(str(tmp_path), "exp", cp_custom, filename="ac-checkpoint.json")
        # Both exist
        assert load_checkpoint(str(tmp_path), "exp") is not None
        assert (
            load_checkpoint(str(tmp_path), "exp", filename="ac-checkpoint.json")
            is not None
        )
        # Clear custom only
        clear_checkpoint(str(tmp_path), "exp", filename="ac-checkpoint.json")
        # Default untouched
        default = load_checkpoint(str(tmp_path), "exp")
        assert default is not None
        assert default.batch_id == "batch-1"
        # Custom gone
        assert (
            load_checkpoint(str(tmp_path), "exp", filename="ac-checkpoint.json") is None
        )
