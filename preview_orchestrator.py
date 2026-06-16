from pathlib import Path

from report_builder import build_report_text
from report_context_factory import ReportContext
from weekly_report_pipeline import run_weekly_report_pipeline


def run_preview_pipeline(excel_path: Path, context: ReportContext) -> str:
    built_report = run_weekly_report_pipeline(excel_path, context)
    return build_report_text(built_report)