"""Tests for backend.runtime.job_runner — RED phase."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.runtime.job_runner import run_daily_job


class TestRunDailyJob:
    @pytest.mark.asyncio
    async def test_calls_orchestrator(self) -> None:
        mock_orchestrator = AsyncMock()
        mock_report = MagicMock()
        mock_report.report_id = "rpt-2026-02-28"
        mock_orchestrator.run_daily_research.return_value = mock_report

        with patch(
            "backend.runtime.job_runner._build_orchestrator",
            return_value=mock_orchestrator,
        ):
            await run_daily_job("2026-02-28")
            mock_orchestrator.run_daily_research.assert_called_once_with(
                "2026-02-28"
            )
