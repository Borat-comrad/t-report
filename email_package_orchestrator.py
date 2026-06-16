from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from detail_excel_builder import build_detail_excel_file
from email_body_builder import build_email_body, build_email_subject
from metrics_reference_docx_builder import build_metrics_reference_docx_file
from report_context_factory import ReportContext
from summary_docx_builder import build_summary_docx_file
from weekly_report_pipeline import run_weekly_report_pipeline


LogFn = Callable[[str], None]


def noop_log(message: str) -> None:
    return None


@dataclass(frozen=True)
class BuiltEmailPackage:
    subject: str
    body: str
    email_text_path: Path
    summary_docx_path: Path
    details_xlsx_path: Path
    metrics_reference_docx_path: Path

    def as_paths_dict(self) -> dict[str, Path]:
        return {
            "email_text": self.email_text_path,
            "summary_docx": self.summary_docx_path,
            "details_xlsx": self.details_xlsx_path,
            "metrics_reference_docx": self.metrics_reference_docx_path,
        }


def write_email_message_file(subject: str, body: str, output_path: Path) -> Path:
    output_text = f"Subject: {subject}\n\n{body}"
    output_path.write_text(output_text, encoding="utf-8")
    return output_path


def run_build_email_package(
    excel_path: Path,
    context: ReportContext,
    output_dir: Path,
    log: LogFn = noop_log,
) -> BuiltEmailPackage:
    log(f"Build step: preparing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    log(f"Build step: reading Excel and calculating metrics: {excel_path}")
    report = run_weekly_report_pipeline(excel_path, context)
    log("Build step: report data calculated.")

    log("Build step: creating email subject and body.")
    subject = build_email_subject(report)
    body = build_email_body(report)

    date_text = context.report_date.isoformat()

    email_text_path = output_dir / f"weekly_report_email_{date_text}.txt"
    summary_docx_path = output_dir / f"weekly_report_summary_{date_text}.docx"
    detail_excel_path = output_dir / f"weekly_report_details_{date_text}.xlsx"
    metrics_reference_docx_path = output_dir / f"weekly_report_metrics_reference_{date_text}.docx"

    log(f"Build step: writing email text file: {email_text_path}")
    write_email_message_file(subject, body, email_text_path)

    log(f"Build step: writing summary DOCX: {summary_docx_path}")
    build_summary_docx_file(report, summary_docx_path)

    log(f"Build step: writing details XLSX: {detail_excel_path}")
    build_detail_excel_file(report, detail_excel_path)

    log(f"Build step: writing metrics reference DOCX: {metrics_reference_docx_path}")
    build_metrics_reference_docx_file(metrics_reference_docx_path)

    log("Build step: email package built successfully.")

    return BuiltEmailPackage(
        subject=subject,
        body=body,
        email_text_path=email_text_path,
        summary_docx_path=summary_docx_path,
        details_xlsx_path=detail_excel_path,
        metrics_reference_docx_path=metrics_reference_docx_path,
    )
