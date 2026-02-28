"""Tests for src.types.ids — RED phase."""

from backend.types.ids import EngineResultId, ReportId, RunId


class TestNewTypes:
    def test_report_id_is_str(self) -> None:
        rid: ReportId = ReportId("rpt-001")
        assert isinstance(rid, str)
        assert rid == "rpt-001"

    def test_run_id_is_str(self) -> None:
        run: RunId = RunId("run-abc")
        assert isinstance(run, str)
        assert run == "run-abc"

    def test_engine_result_id_is_str(self) -> None:
        eid: EngineResultId = EngineResultId("er-xyz")
        assert isinstance(eid, str)
        assert eid == "er-xyz"
