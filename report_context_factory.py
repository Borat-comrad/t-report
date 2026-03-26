from dataclasses import dataclass
from datetime import date, timedelta

from cli_parser import CliCommand, RunMode


@dataclass(frozen=True)
class ReportContext:
    mode: RunMode
    report_date: date
    current_week_start: date
    current_week_end: date
    next_two_weeks_start: date
    next_two_weeks_end: date
    run_id: str


class ReportContextError(Exception):
    """Ошибка построения контекста отчёта."""

def get_monday(input_date: date) -> date:
    days_from_monday = input_date.weekday()
    return input_date - timedelta(days=days_from_monday)


def get_sunday(input_date: date) -> date:
    days_to_sunday = 6 - input_date.weekday()
    return input_date + timedelta(days=days_to_sunday)


def resolve_report_date(command: CliCommand, current_date: date) -> date:
    if command.date_raw is not None:
        try:
            return date.fromisoformat(command.date_raw)
        except ValueError as exc:
            raise ReportContextError(
                "Некорректный формат даты отчёта. Ожидается YYYY-MM-DD."
            ) from exc

    return get_monday(current_date)


def build_report_context(command: CliCommand, current_date: date) -> ReportContext:
    report_date = resolve_report_date(command, current_date)

    current_week_start = get_monday(report_date)
    current_week_end = get_sunday(report_date)

    next_two_weeks_start = current_week_start + timedelta(days=7)
    next_two_weeks_end = current_week_end + timedelta(days=14)

    run_id = f"{command.mode.value}:{report_date.isoformat()}"

    return ReportContext(
        mode=command.mode,
        report_date=report_date,
        current_week_start=current_week_start,
        current_week_end=current_week_end,
        next_two_weeks_start=next_two_weeks_start,
        next_two_weeks_end=next_two_weeks_end,
        run_id=run_id,
    )