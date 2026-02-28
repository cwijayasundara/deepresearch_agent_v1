"""Tests for src.service.report_parser — RED phase."""

from backend.service.report_parser import ReportParser


SAMPLE_MARKDOWN = """# Global AI Viral Intelligence Tracker v4.0

## TL;DR
- GPT-5 released with multimodal capabilities
- Google announces Gemini 3.0
- EU AI Act enforcement begins

## Global Viral Events

### GPT-5 Released
- **Category**: product_launch
- **Impact Rating**: 9
- **Confidence**: high
- **Source**: OpenAI Blog

### Gemini 3.0 Announced
- **Category**: product_launch
- **Impact Rating**: 8
- **Confidence**: high
- **Source**: Google AI Blog

## Strategic Deep Dives

### Multimodal AI Race
- **Priority**: HIGH
- **Summary**: The competition between OpenAI and Google intensifies.
- **Key Findings**:
  - Both models support vision and audio
  - Pricing war emerging

### EU Regulation Impact
- **Priority**: MEDIUM
- **Summary**: New regulations reshape AI deployment in Europe.
- **Key Findings**:
  - Compliance costs rising
  - Smaller companies affected most

## Completeness Audit
- **Verified Signals**: 42
- **Sources Checked**: 15
- **Confidence Score**: 0.87
- **Gaps**: Missing Asian market data, Limited startup coverage
"""


class TestReportParser:
    def setup_method(self) -> None:
        self.parser = ReportParser()

    def test_parse_tldr(self) -> None:
        result = self.parser.parse_tldr(SAMPLE_MARKDOWN)
        assert "GPT-5" in result

    def test_parse_viral_events(self) -> None:
        events = self.parser.parse_viral_events(SAMPLE_MARKDOWN)
        assert len(events) >= 1
        assert events[0].headline == "GPT-5 Released"

    def test_parse_deep_dives(self) -> None:
        dives = self.parser.parse_deep_dives(SAMPLE_MARKDOWN)
        assert len(dives) >= 1
        assert dives[0].title == "Multimodal AI Race"

    def test_parse_completeness_audit(self) -> None:
        audit = self.parser.parse_completeness_audit(SAMPLE_MARKDOWN)
        assert audit is not None
        assert audit.verified_signals == 42
        assert audit.sources_checked == 15
        assert audit.confidence_score == 0.87

    def test_parse_tldr_missing_section(self) -> None:
        result = self.parser.parse_tldr("# No TL;DR here")
        assert result == ""

    def test_parse_viral_events_empty(self) -> None:
        events = self.parser.parse_viral_events("# Nothing")
        assert events == []
