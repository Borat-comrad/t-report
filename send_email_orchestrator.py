from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from email_package_orchestrator import BuiltEmailPackage, run_build_email_package
from email_sender import load_smtp_settings, send_email_package
from report_context_factory import ReportContext


LogFn = Callable[[str], None]


def noop_log(message: str) -> None:
    return None


@dataclass(frozen=True)
class SentEmailResult:
    package: BuiltEmailPackage
    recipients: tuple[str, ...]


def run_send_email_report(
    excel_path: Path,
    context: ReportContext,
    output_dir: Path,
    email_to_raw: str | None,
    log: LogFn = noop_log,
) -> SentEmailResult:
    log("Send step: building email package.")
    package = run_build_email_package(
        excel_path=excel_path,
        context=context,
        output_dir=output_dir,
        log=log,
    )

    log("Send step: loading SMTP settings.")
    smtp_settings = load_smtp_settings(email_to_raw, log=log)

    log("Send step: sending message to SMTP server.")
    send_email_package(smtp_settings, package, log=log)
    log("Send step: SMTP server accepted the message.")

    return SentEmailResult(
        package=package,
        recipients=smtp_settings.to_addresses,
    )
