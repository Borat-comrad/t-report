from __future__ import annotations

from collections.abc import Callable
import os
import re
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from email_package_orchestrator import BuiltEmailPackage


LogFn = Callable[[str], None]


def noop_log(message: str) -> None:
    return None


class EmailSendError(Exception):
    """Email configuration or sending error."""


@dataclass(frozen=True)
class SmtpSettings:
    host: str
    port: int
    username: str
    password: str
    from_address: str
    to_addresses: tuple[str, ...]
    security_mode: str


def parse_recipients(raw_value: str) -> tuple[str, ...]:
    recipients = tuple(
        email.strip()
        for email in re.split(r"[,;\r\n]+", raw_value)
        if email.strip() != ""
    )

    if not recipients:
        raise EmailSendError("No email recipient address was provided.")

    return recipients


def read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value == "":
        raise EmailSendError(f"Required environment variable is missing: {name}.")
    return value


def parse_port(raw_value: str) -> int:
    try:
        return int(raw_value)
    except ValueError as exc:
        raise EmailSendError("SMTP port must be an integer.") from exc


def normalize_security_mode(raw_value: str) -> str:
    security_mode = raw_value.strip().lower()
    if security_mode not in {"starttls", "ssl", "none"}:
        raise EmailSendError(
            "T_REPORT_SMTP_SECURITY must be one of: starttls, ssl, none."
        )
    return security_mode


def load_smtp_settings(explicit_to_raw: str | None, log: LogFn = noop_log) -> SmtpSettings:
    host = read_required_env("T_REPORT_SMTP_HOST")
    port = parse_port(os.getenv("T_REPORT_SMTP_PORT", "587"))
    username = read_required_env("T_REPORT_SMTP_USERNAME")
    password = read_required_env("T_REPORT_SMTP_PASSWORD")
    from_address = os.getenv("T_REPORT_EMAIL_FROM", username).strip() or username

    recipient_source = explicit_to_raw
    if recipient_source is None or recipient_source.strip() == "":
        recipient_source = read_required_env("T_REPORT_EMAIL_TO")

    to_addresses = parse_recipients(recipient_source)
    security_mode = normalize_security_mode(os.getenv("T_REPORT_SMTP_SECURITY", "starttls"))

    log(
        "SMTP settings loaded: "
        f"host={host}, port={port}, security={security_mode}, "
        f"from={from_address}, recipients={len(to_addresses)}."
    )

    return SmtpSettings(
        host=host,
        port=port,
        username=username,
        password=password,
        from_address=from_address,
        to_addresses=to_addresses,
        security_mode=security_mode,
    )


def attach_file(message: EmailMessage, file_path: Path, log: LogFn = noop_log) -> None:
    if not file_path.exists():
        raise EmailSendError(f"Attachment file was not found: {file_path}")

    attachment_bytes = file_path.read_bytes()
    log(f"Email step: attaching {file_path.name}, bytes={len(attachment_bytes)}.")

    if file_path.suffix.lower() == ".docx":
        maintype = "application"
        subtype = "vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_path.suffix.lower() == ".xlsx":
        maintype = "application"
        subtype = "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        maintype = "application"
        subtype = "octet-stream"

    message.add_attachment(
        attachment_bytes,
        maintype=maintype,
        subtype=subtype,
        filename=file_path.name,
    )


def build_email_message(
    settings: SmtpSettings,
    package: BuiltEmailPackage,
    log: LogFn = noop_log,
) -> EmailMessage:
    log("Email step: building MIME message.")
    message = EmailMessage()
    message["Subject"] = package.subject
    message["From"] = settings.from_address
    message["To"] = ", ".join(settings.to_addresses)
    message.set_content(package.body)

    attach_file(message, package.summary_docx_path, log=log)
    attach_file(message, package.details_xlsx_path, log=log)
    attach_file(message, package.metrics_reference_docx_path, log=log)

    return message


def send_email_package(
    settings: SmtpSettings,
    package: BuiltEmailPackage,
    log: LogFn = noop_log,
) -> None:
    message = build_email_message(settings, package, log=log)

    if settings.security_mode == "ssl":
        smtp_factory = smtplib.SMTP_SSL
    else:
        smtp_factory = smtplib.SMTP

    try:
        log(f"SMTP step: connecting to {settings.host}:{settings.port}.")
        with smtp_factory(settings.host, settings.port, timeout=30) as smtp:
            log("SMTP step: connected; sending EHLO.")
            smtp.ehlo()

            if settings.security_mode == "starttls":
                log("SMTP step: starting STARTTLS.")
                smtp.starttls()
                smtp.ehlo()

            log(f"SMTP step: logging in as {settings.username}.")
            smtp.login(settings.username, settings.password)
            log("SMTP step: sending message.")
            smtp.send_message(message)
            log("SMTP step: message accepted without SMTP error.")
    except OSError as exc:
        raise EmailSendError(f"Could not connect to SMTP server: {exc}") from exc
    except smtplib.SMTPException as exc:
        raise EmailSendError(f"SMTP error while sending email: {exc}") from exc
