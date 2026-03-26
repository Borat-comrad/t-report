import argparse
from dataclasses import dataclass
from enum import Enum

class RunMode(str, Enum):
    PREVIEW = "preview"
    SEND = "send"

@dataclass(frozen=True)
class CliCommand:
    mode: RunMode
    date_raw: str | None = None

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
        help="Сформировать отчёт и отправить его."
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Дата отчёта в формате YYYY-MM-DD."
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
    else:
        raise CliParseError("Не удалось определить режим запуска.")

    return CliCommand(
        mode=mode,
        date_raw=namespace.date
    )

