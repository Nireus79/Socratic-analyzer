"""Tests for analytics export module."""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from socratic_analyzer.analytics_export import (
    AnalyticsExporter,
    ReportGenerator,
    ScheduledExporter,
)


class TestAnalyticsExporter:
    """Test AnalyticsExporter class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for exports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def exporter(self, temp_dir):
        """Create exporter with temp directory."""
        return AnalyticsExporter(temp_dir)

    @pytest.mark.asyncio
    async def test_initialization(self, temp_dir):
        """Test exporter initialization creates directory."""
        exporter = AnalyticsExporter(temp_dir)
        assert exporter.output_dir.exists()

    @pytest.mark.asyncio
    async def test_export_to_json(self, exporter):
        """Test exporting data to JSON."""
        data = {"key": "value", "number": 42}
        filepath = await exporter.export_to_json(data, "test_data")

        assert Path(filepath).exists()
        with open(filepath) as f:
            exported = json.load(f)
        assert exported == data

    @pytest.mark.asyncio
    async def test_export_to_json_with_datetime(self, exporter):
        """Test exporting JSON with datetime objects."""
        from datetime import datetime

        data = {"timestamp": datetime.now(), "value": 123}
        filepath = await exporter.export_to_json(data, "test_datetime")

        assert Path(filepath).exists()

    @pytest.mark.asyncio
    async def test_export_to_csv_with_data(self, exporter):
        """Test exporting data to CSV."""
        data = [
            {"name": "Alice", "score": 95},
            {"name": "Bob", "score": 87},
        ]
        filepath = await exporter.export_to_csv(data, "test_csv")

        assert Path(filepath).exists()
        with open(filepath) as f:
            content = f.read()
        assert "Alice" in content
        assert "Bob" in content

    @pytest.mark.asyncio
    async def test_export_to_csv_empty_data(self, exporter):
        """Test exporting empty CSV."""
        filepath = await exporter.export_to_csv([], "empty_csv")

        assert filepath is not None

    @pytest.mark.asyncio
    async def test_export_to_csv_custom_fieldnames(self, exporter):
        """Test exporting CSV with custom fieldnames."""
        data = [{"a": 1, "b": 2}]
        filepath = await exporter.export_to_csv(
            data, "custom_fields", fieldnames=["a", "b"]
        )

        assert Path(filepath).exists()

    @pytest.mark.asyncio
    async def test_export_to_pdf(self, exporter):
        """Test exporting to PDF."""
        content = "Test PDF content"
        filepath = await exporter.export_to_pdf(content, "test_pdf")

        assert filepath is not None


class TestReportGenerator:
    """Test ReportGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create report generator."""
        return ReportGenerator()

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test generator initialization."""
        generator = ReportGenerator()
        assert generator.reports == {}

    @pytest.mark.asyncio
    async def test_generate_user_analytics_report(self, generator):
        """Test generating user analytics report."""
        metrics = {
            "total_sessions": 10,
            "total_questions_answered": 50,
            "completion_rate": 0.85,
        }
        report = await generator.generate_user_analytics_report("user123", metrics)

        assert report["user_id"] == "user123"
        assert report["summary"]["total_sessions"] == 10
        assert report["summary"]["total_questions"] == 50
        assert report["summary"]["completion_rate"] == 0.85
        assert "report_id" in report
        assert "generated_at" in report

    @pytest.mark.asyncio
    async def test_generate_user_report_missing_metrics(self, generator):
        """Test user report with missing metrics."""
        metrics = {"total_sessions": 5}
        report = await generator.generate_user_analytics_report("user456", metrics)

        assert report["summary"]["total_sessions"] == 5
        assert report["summary"]["total_questions"] == 0
        assert report["summary"]["completion_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_generate_cohort_analytics_report(self, generator):
        """Test generating cohort analytics report."""
        users_metrics = [
            {"total_sessions": 10, "total_questions_answered": 50, "completion_rate": 0.8},
            {"total_sessions": 15, "total_questions_answered": 60, "completion_rate": 0.9},
        ]
        report = await generator.generate_cohort_analytics_report("cohort_a", users_metrics)

        assert report["cohort_name"] == "cohort_a"
        assert report["total_users"] == 2
        assert report["summary"]["total_sessions"] == 25
        assert report["summary"]["total_questions"] == 110
        assert abs(report["summary"]["average_completion_rate"] - 0.85) < 0.0001

    @pytest.mark.asyncio
    async def test_generate_cohort_report_empty(self, generator):
        """Test cohort report with no users."""
        report = await generator.generate_cohort_analytics_report("empty_cohort", [])

        assert report["total_users"] == 0
        assert report["summary"]["average_completion_rate"] == 0

    @pytest.mark.asyncio
    async def test_reports_stored(self, generator):
        """Test reports are stored in generator."""
        metrics = {"total_sessions": 5, "total_questions_answered": 20, "completion_rate": 0.75}
        report = await generator.generate_user_analytics_report("user789", metrics)

        assert report["report_id"] in generator.reports
        assert generator.reports[report["report_id"]] == report

    @pytest.mark.asyncio
    async def test_export_report_json(self, generator):
        """Test exporting generated report as JSON."""
        metrics = {"total_sessions": 10, "total_questions_answered": 50, "completion_rate": 0.85}
        report = await generator.generate_user_analytics_report("user_export", metrics)

        # Should not raise
        filepath = await generator.export_report(report["report_id"], "json")
        assert filepath is not None

    @pytest.mark.asyncio
    async def test_export_report_csv(self, generator):
        """Test exporting generated report as CSV."""
        metrics = {"total_sessions": 10, "total_questions_answered": 50, "completion_rate": 0.85}
        report = await generator.generate_user_analytics_report("user_csv", metrics)

        filepath = await generator.export_report(report["report_id"], "csv")
        assert filepath is not None

    @pytest.mark.asyncio
    async def test_export_nonexistent_report(self, generator):
        """Test exporting non-existent report raises error."""
        with pytest.raises(ValueError):
            await generator.export_report("nonexistent_id", "json")

    @pytest.mark.asyncio
    async def test_export_unsupported_format(self, generator):
        """Test exporting with unsupported format raises error."""
        metrics = {"total_sessions": 5, "total_questions_answered": 20, "completion_rate": 0.75}
        report = await generator.generate_user_analytics_report("user_format", metrics)

        with pytest.raises(ValueError):
            await generator.export_report(report["report_id"], "xml")


class TestScheduledExporter:
    """Test ScheduledExporter class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def exporter(self, temp_dir):
        """Create exporter."""
        return AnalyticsExporter(temp_dir)

    @pytest.fixture
    def scheduled_exporter(self, exporter):
        """Create scheduled exporter."""
        return ScheduledExporter(exporter)

    @pytest.mark.asyncio
    async def test_initialization(self, exporter):
        """Test scheduled exporter initialization."""
        scheduler = ScheduledExporter(exporter)
        assert scheduler.exporter == exporter
        assert scheduler.scheduled_exports == {}
        assert scheduler.running is False

    @pytest.mark.asyncio
    async def test_schedule_export(self, scheduled_exporter):
        """Test scheduling an export."""
        async def data_source():
            return {"data": "test"}

        await scheduled_exporter.schedule_export("export1", 24, data_source, "json")

        assert "export1" in scheduled_exporter.scheduled_exports
        assert scheduled_exporter.scheduled_exports["export1"]["interval_hours"] == 24

    @pytest.mark.asyncio
    async def test_schedule_multiple_exports(self, scheduled_exporter):
        """Test scheduling multiple exports."""
        async def data_source1():
            return {"data": "test1"}

        async def data_source2():
            return {"data": "test2"}

        await scheduled_exporter.schedule_export("export1", 24, data_source1)
        await scheduled_exporter.schedule_export("export2", 12, data_source2)

        assert len(scheduled_exporter.scheduled_exports) == 2

    @pytest.mark.asyncio
    async def test_stop_scheduler(self, scheduled_exporter):
        """Test stopping scheduler."""
        scheduled_exporter.running = True
        await scheduled_exporter.stop_scheduler()

        assert scheduled_exporter.running is False

    @pytest.mark.asyncio
    async def test_scheduler_start_stop_cycle(self, scheduled_exporter):
        """Test starting and stopping scheduler."""
        async def data_source():
            return {"data": "test"}

        await scheduled_exporter.schedule_export("quick_export", 1, data_source)

        # Create a task that runs for a short time then stops
        async def run_scheduler_briefly():
            scheduler_task = asyncio.create_task(scheduled_exporter.start_scheduler())
            await asyncio.sleep(0.1)
            await scheduled_exporter.stop_scheduler()
            await scheduler_task

        # Should complete without error
        await run_scheduler_briefly()
