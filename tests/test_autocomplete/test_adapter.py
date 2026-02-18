"""Tests for autocomplete adapter loading."""

from __future__ import annotations

import textwrap

import pytest

from veritail.autocomplete.adapter import load_suggest_adapter


class TestLoadSuggestAdapter:
    def test_valid_adapter(self, tmp_path) -> None:
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            textwrap.dedent("""\
            def suggest(prefix):
                return ["suggestion1", "suggestion2"]
            """)
        )
        fn = load_suggest_adapter(str(adapter_file))
        response = fn("test")
        assert response.suggestions == ["suggestion1", "suggestion2"]

    def test_adapter_returns_autocomplete_response(self, tmp_path) -> None:
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            textwrap.dedent("""\
            from veritail.types import AutocompleteResponse

            def suggest(prefix):
                return AutocompleteResponse(
                    suggestions=["a", "b"],
                    metadata={"source": "test"},
                )
            """)
        )
        fn = load_suggest_adapter(str(adapter_file))
        response = fn("test")
        assert response.suggestions == ["a", "b"]
        assert response.metadata == {"source": "test"}

    def test_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_suggest_adapter("/nonexistent/adapter.py")

    def test_non_python_file(self, tmp_path) -> None:
        txt_file = tmp_path / "adapter.txt"
        txt_file.write_text("not python")
        with pytest.raises(ValueError, match="Python file"):
            load_suggest_adapter(str(txt_file))

    def test_missing_suggest_function(self, tmp_path) -> None:
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("x = 1\n")
        with pytest.raises(AttributeError, match="suggest"):
            load_suggest_adapter(str(adapter_file))

    def test_suggest_not_callable(self, tmp_path) -> None:
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("suggest = 42\n")
        with pytest.raises(TypeError, match="not callable"):
            load_suggest_adapter(str(adapter_file))
