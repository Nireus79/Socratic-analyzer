"""Analytics export for socratic-analyzer."""
import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalyticsExporter:
    """Export analytics data in multiple formats."""

    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export data to JSON file."""
        filepath = self.output_dir / f"{filename}.json"
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Exported JSON to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            raise

    async def export_to_csv(
        self, data: List[Dict[str, Any]], filename: str, fieldnames: Optional[List[str]] = None
    ) -> str:
        """Export data to CSV file."""
        filepath = self.output_dir / f"{filename}.csv"
        try:
            if not data:
                logger.warning("No data to export")
                return str(filepath)

            if fieldnames is None:
                fieldnames = list(data[0].keys())

            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    clean_row = {
                        k: str(v) if not isinstance(v, (int, float)) else v for k, v in row.items()
                    }
                    writer.writerow(clean_row)

            logger.info(f"Exported CSV to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise

    async def export_to_pdf(self, content: str, filename: str) -> str:
        """Export content to PDF file."""
        filepath = self.output_dir / f"{filename}.pdf"
        try:
            logger.info(f"PDF export would be created at {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise


class ReportGenerator:
    """Generate analytics reports."""

    def __init__(self):
        self.reports: Dict[str, Dict[str, Any]] = {}

    async def generate_user_analytics_report(
        self, user_id: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate user analytics report."""
        report = {
            "report_id": f"user_{user_id}_{datetime.now().isoformat()}",
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "summary": {
                "total_sessions": metrics.get("total_sessions", 0),
                "total_questions": metrics.get("total_questions_answered", 0),
                "completion_rate": metrics.get("completion_rate", 0.0),
            },
        }
        self.reports[report["report_id"]] = report
        logger.info(f"Generated report {report['report_id']}")
        return report

    async def generate_cohort_analytics_report(
        self, cohort_name: str, users_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate cohort analytics report."""
        total_users = len(users_metrics)
        avg_completion = (
            sum(m.get("completion_rate", 0) for m in users_metrics) / total_users
            if total_users > 0
            else 0
        )

        report = {
            "report_id": f"cohort_{cohort_name}_{datetime.now().isoformat()}",
            "cohort_name": cohort_name,
            "generated_at": datetime.now().isoformat(),
            "total_users": total_users,
            "summary": {
                "average_completion_rate": avg_completion,
                "total_sessions": sum(m.get("total_sessions", 0) for m in users_metrics),
                "total_questions": sum(m.get("total_questions_answered", 0) for m in users_metrics),
            },
        }
        self.reports[report["report_id"]] = report
        return report

    async def export_report(self, report_id: str, format: str = "json") -> str:
        """Export a generated report."""
        if report_id not in self.reports:
            raise ValueError(f"Report {report_id} not found")

        report = self.reports[report_id]
        exporter = AnalyticsExporter()

        if format == "json":
            return await exporter.export_to_json(report, report_id)
        elif format == "csv":
            return await exporter.export_to_csv([report], report_id)
        else:
            raise ValueError(f"Unsupported format: {format}")


class ScheduledExporter:
    """Schedule periodic exports."""

    def __init__(self, exporter: AnalyticsExporter):
        self.exporter = exporter
        self.scheduled_exports: Dict[str, Dict[str, Any]] = {}
        self.running = False

    async def schedule_export(
        self, export_id: str, interval_hours: int, data_source, format: str = "json"
    ) -> None:
        """Schedule periodic export."""
        self.scheduled_exports[export_id] = {
            "interval_hours": interval_hours,
            "data_source": data_source,
            "format": format,
            "last_export": None,
        }
        logger.info(f"Scheduled export {export_id} every {interval_hours} hours")

    async def start_scheduler(self) -> None:
        """Start running scheduled exports."""
        self.running = True
        while self.running:
            for export_id, config in self.scheduled_exports.items():
                last = config.get("last_export")
                if last is None or (datetime.now() - last).total_seconds() > (
                    config["interval_hours"] * 3600
                ):
                    try:
                        data = await config["data_source"]()
                        await self.exporter.export_to_json(
                            data, f"{export_id}_{datetime.now().isoformat()}"
                        )
                        config["last_export"] = datetime.now()
                    except Exception as e:
                        logger.error(f"Failed to execute scheduled export {export_id}: {e}")

            await asyncio.sleep(60)

    async def stop_scheduler(self) -> None:
        """Stop scheduler."""
        self.running = False
        logger.info("Scheduled exporter stopped")
