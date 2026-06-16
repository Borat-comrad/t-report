import argparse
from dataclasses import dataclass
from enum import Enum


class RunMode(str, Enum):
    PREVIEW = "preview"
    SEND = "send"
    BUILD_EMAIL_PACKAGE = "build_email_package"


@dataclass(frozen=True)
class CliCommand:
    mode: RunMode
    date_raw: str | None = None
    excel_path_raw: str | None = None
    google_spreadsheet_id_raw: str | None = None
    google_credentials_path_raw: str | None = None
    google_snapshot_dir_raw: str | None = None
    output_dir_raw: str | None = None
    email_to_raw: str | None = None


class CliParseError(Exception):
    """Ошибка разбора аргументов командной строки."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="report_tool",
        description="Формирование отчёта по КП и поставкам."
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        "--preview",
        action="store_true",
        help="Сформировать отчёт и вывести его в консоль."
    )

    mode_group.add_argument(
        "--send",
        action="store_true",
        help="Сформировать отчёт и отправить его по email через SMTP."
    )

    mode_group.add_argument(
        "--build-email-package",
        action="store_true",
        help="Собрать локальный email-пакет: текст письма, DOCX и XLSX."
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Дата отчёта в формате YYYY-MM-DD."
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        help="Папка для сохранения локально собранного email-пакета."
    )

    parser.add_argument(
        "--excel-path",
        type=str,
        help="Путь к исходному Excel-файлу. Если не указан, используется DS.xlsx в папке проекта."
    )

    parser.add_argument(
        "--google-spreadsheet-id",
        type=str,
        help="ID Google Sheets таблицы, которую нужно скачать как XLSX перед расчетом."
    )

    parser.add_argument(
        "--google-credentials-path",
        type=str,
        help="Путь к JSON-ключу Google service account."
    )

    parser.add_argument(
        "--google-snapshot-dir",
        type=str,
        help="Папка для XLSX-снапшотов, скачанных из Google Sheets."
    )

    parser.add_argument(
        "--email-to",
        type=str,
        help="Получатели email через запятую. Если не указано, будет использована T_REPORT_EMAIL_TO."
    )

    return parser


def parse_cli(args: list[str]) -> CliCommand:
    parser = build_parser()

    try:
        namespace = parser.parse_args(args)
    except SystemExit as exc:
        raise CliParseError("Некорректные аргументы командной строки.") from exc

    if namespace.preview:
        mode = RunMode.PREVIEW
    elif namespace.send:
        mode = RunMode.SEND
    elif namespace.build_email_package:
        mode = RunMode.BUILD_EMAIL_PACKAGE
    else:
        raise CliParseError("Не удалось определить режим запуска.")

    return CliCommand(
        mode=mode,
        date_raw=namespace.date,
        excel_path_raw=namespace.excel_path,
        google_spreadsheet_id_raw=namespace.google_spreadsheet_id,
        google_credentials_path_raw=namespace.google_credentials_path,
        google_snapshot_dir_raw=namespace.google_snapshot_dir,
        output_dir_raw=namespace.output_dir,
        email_to_raw=namespace.email_to,
    )
