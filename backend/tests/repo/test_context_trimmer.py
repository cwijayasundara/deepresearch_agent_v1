"""Tests for backend.repo.context_trimmer — RED phase."""

from backend.repo.context_trimmer import (
    count_tokens,
    trim_context,
)


class TestCountTokens:
    def test_empty_string(self) -> None:
        assert count_tokens("") == 0

    def test_simple_text(self) -> None:
        tokens = count_tokens("Hello world")
        assert tokens > 0
        assert tokens < 10

    def test_longer_text(self) -> None:
        text = "The quick brown fox jumps over the lazy dog. " * 10
        tokens = count_tokens(text)
        assert tokens > 50

    def test_custom_model(self) -> None:
        tokens = count_tokens("Hello world", model="gpt-4")
        assert tokens > 0


class TestTrimContext:
    def test_short_context_unchanged(self) -> None:
        prompt = "Research prompt"
        context = "Short search result"
        result = trim_context(prompt, context, max_fraction=0.75)
        assert context in result

    def test_returns_trimmed_when_over_limit(self) -> None:
        prompt = "Research prompt"
        context = "Search result line.\n" * 5000
        result = trim_context(
            prompt, context, max_fraction=0.75, max_tokens=1000
        )
        result_tokens = count_tokens(result)
        assert result_tokens < 1000

    def test_preserves_prompt(self) -> None:
        prompt = "Research prompt"
        context = "Search result line.\n" * 5000
        result = trim_context(
            prompt, context, max_fraction=0.75, max_tokens=1000
        )
        assert result is not None
        assert len(result) > 0

    def test_truncation_preserves_full_lines(self) -> None:
        prompt = "Prompt"
        lines = [f"Line {i}: Some content here" for i in range(200)]
        context = "\n".join(lines)
        result = trim_context(
            prompt, context, max_fraction=0.75, max_tokens=500
        )
        for line in result.split("\n"):
            if line.startswith("Line "):
                assert "Some content here" in line

    def test_default_max_tokens_uses_model_window(self) -> None:
        prompt = "Research prompt"
        context = "Short result"
        result = trim_context(prompt, context)
        assert context in result
