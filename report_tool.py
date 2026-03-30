from datetime import date
from pathlib import Path
import sys

from cli_parser import CliParseError, RunMode, parse_cli
from console_output import print_report
from preview_orchestrator import run_preview_pipeline
from report_context_factory import ReportContextError, build_report_context


DEFAULT_EXCEL_PATH = Path(__file__).with_name("DS.xlsx")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    try:
        command = parse_cli(argv)
        context = build_report_context(command, date.today())
        report_text = run_preview_pipeline(DEFAULT_EXCEL_PATH, context)
    except (CliParseError, ReportContextError, Exception) as exc:
        print(f"Ошибка запуска демо: {exc}", file=sys.stderr)
        return 1

    if command.mode is RunMode.SEND:
        print("SEND-режим в демке не подключён к Telegram. Ниже — собранный отчёт.\n")

    print_report(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
