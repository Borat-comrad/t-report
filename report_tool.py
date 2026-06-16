from collections.abc import Callable
from datetime import date
from pathlib import Path
import sys

from cli_parser import CliParseError, RunMode, parse_cli
from console_output import print_report
from email_package_orchestrator import BuiltEmailPackage, run_build_email_package
from email_sender import EmailSendError
from google_sheets_source import (
    GoogleSheetsConfig,
    GoogleSheetsSourceError,
    download_google_sheet_snapshot,
    load_google_sheets_config_from_env,
)
from preview_orchestrator import run_preview_pipeline
from report_context_factory import ReportContextError, build_report_context
from send_email_orchestrator import SentEmailResult, run_send_email_report


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXCEL_PATH = BASE_DIR / "DS.xlsx"
DEFAULT_INPUT_DIR = BASE_DIR / "input"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"
LogFn = Callable[[str], None]


try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


def log_event(message: str) -> None:
    print(message, flush=True)


def noop_log(message: str) -> None:
    return None


def print_built_email_package(package: BuiltEmailPackage) -> None:
    print("Email package built successfully.\n")
    print(f"Email text: {package.email_text_path}")
    print(f"Summary DOCX: {package.summary_docx_path}")
    print(f"Details XLSX: {package.details_xlsx_path}")
    print(f"Metrics reference DOCX: {package.metrics_reference_docx_path}")


def print_sent_email_result(result: SentEmailResult) -> None:
    recipients_text = ", ".join(result.recipients)

    print("Email sent successfully.\n")
    print(f"Recipients: {recipients_text}")
    print(f"Email text copy: {result.package.email_text_path}")
    print(f"Attached DOCX: {result.package.summary_docx_path}")
    print(f"Attached XLSX: {result.package.details_xlsx_path}")
    print(f"Attached metrics reference DOCX: {result.package.metrics_reference_docx_path}")


def build_google_sheets_config(command) -> GoogleSheetsConfig | None:
    env_config = load_google_sheets_config_from_env(BASE_DIR)

    spreadsheet_id = (
        command.google_spreadsheet_id_raw
        or (env_config.spreadsheet_id if env_config is not None else "")
    )
    credentials_path_raw = (
        command.google_credentials_path_raw
        or (str(env_config.credentials_path) if env_config is not None else "")
    )
    snapshot_dir_raw = (
        command.google_snapshot_dir_raw
        or (str(env_config.snapshot_dir) if env_config is not None else "")
    )

    if spreadsheet_id == "" and credentials_path_raw == "":
        return None

    if spreadsheet_id == "":
        raise GoogleSheetsSourceError("Google Sheets spreadsheet ID is not configured.")

    if credentials_path_raw == "":
        raise GoogleSheetsSourceError("Google service account JSON path is not configured.")

    return GoogleSheetsConfig(
        spreadsheet_id=spreadsheet_id,
        credentials_path=Path(credentials_path_raw),
        snapshot_dir=Path(snapshot_dir_raw) if snapshot_dir_raw else DEFAULT_INPUT_DIR,
    )


def resolve_excel_path(
    command,
    report_date_text: str,
    log: LogFn = noop_log,
) -> Path:
    log("Data source step: checking Google Sheets configuration.")
    google_config = build_google_sheets_config(command)

    if command.excel_path_raw and google_config is not None:
        raise GoogleSheetsSourceError(
            "Only one data source is allowed: use either --excel-path or Google Sheets."
        )

    if google_config is not None:
        log(
            "Data source step: Google Sheets selected; "
            f"snapshot directory: {google_config.snapshot_dir}."
        )
        excel_path = download_google_sheet_snapshot(
            google_config,
            report_date_text,
            log=log,
        )
        log(f"Data source step: Google Sheets snapshot saved: {excel_path}")
        return excel_path

    excel_path = Path(command.excel_path_raw) if command.excel_path_raw else DEFAULT_EXCEL_PATH
    log(f"Data source step: local Excel selected: {excel_path}")
    return excel_path


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    current_stage = "program startup"

    try:
        log_event("report_tool started.")

        current_stage = "parse command line arguments"
        log_event(f"Startup step: {current_stage}.")
        command = parse_cli(argv)
        log_event(f"Startup step: mode={command.mode.value}.")

        current_stage = "build report date context"
        log_event(f"Startup step: {current_stage}.")
        context = build_report_context(command, date.today())
        log_event(
            "Startup step: "
            f"report_date={context.report_date.isoformat()}, "
            f"week={context.current_week_start.isoformat()}..{context.current_week_end.isoformat()}."
        )

        current_stage = "resolve data source"
        excel_path = resolve_excel_path(command, context.report_date.isoformat(), log=log_event)

        current_stage = "prepare output directory"
        output_dir = Path(command.output_dir_raw) if command.output_dir_raw else DEFAULT_OUTPUT_DIR
        log_event(f"Startup step: output_dir={output_dir}.")

        if command.mode is RunMode.BUILD_EMAIL_PACKAGE:
            current_stage = "build email package without sending"
            log_event(f"Mode step: {current_stage}.")
            built_package = run_build_email_package(
                excel_path=excel_path,
                context=context,
                output_dir=output_dir,
                log=log_event,
            )
            print_built_email_package(built_package)
            log_event("report_tool finished successfully.")
            return 0

        if command.mode is RunMode.SEND:
            current_stage = "build and send email"
            log_event(f"Mode step: {current_stage}.")
            send_result = run_send_email_report(
                excel_path=excel_path,
                context=context,
                output_dir=output_dir,
                email_to_raw=command.email_to_raw,
                log=log_event,
            )
            print_sent_email_result(send_result)
            log_event("report_tool finished successfully.")
            return 0

        current_stage = "build preview report"
        log_event(f"Mode step: {current_stage}.")
        report_text = run_preview_pipeline(excel_path, context)
    except (CliParseError, ReportContextError, EmailSendError, GoogleSheetsSourceError, Exception) as exc:
        print(f"ERROR: stage '{current_stage}' failed: {exc}", flush=True)
        return 1

    print_report(report_text)
    log_event("report_tool finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
