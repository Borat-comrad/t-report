from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Mapping

from data_quality import RowNormalizationSkipped, SourceRowIssue, format_raw_value
from exel_sourse_reader import RawSheets
from structure_validator import RawHeaderMaps


class KpNormalizationError(Exception):
    pass


@dataclass(frozen=True)
class NormalizedKpRow:
    source_row_index: int
    request_number: str
    received_date: date | None
    manufacturer: str
    branch: str
    employee: str
    email_subject: str
    proposal_deadline: date | None
    preparation_status: str


@dataclass(frozen=True)
class KpNormalizationResult:
    rows: list[NormalizedKpRow]
    issues: list[SourceRowIssue]


def normalize_text_value(value: object) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_date_value(value: object) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text_value = normalize_text_value(value)

    if text_value == "":
        return None

    extracted_candidates = [
        match.group(0)
        for match in re.finditer(
            r"\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{2}",
            text_value,
        )
    ]

    if not extracted_candidates and not any(separator in text_value for separator in ("-", ".", "/")):
        return None

    candidate_values = [text_value, *extracted_candidates]

    for candidate in candidate_values:
        for date_format in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
            try:
                return datetime.strptime(candidate, date_format).date()
            except ValueError:
                continue

    raise KpNormalizationError(
        f"Не удалось распознать дату: {text_value}"
    )


def get_cell_value_by_header(
    row_values: tuple[object, ...],
    columns: Mapping[str, int],
    header_name: str,
) -> object:
    column_index = columns[header_name]
    zero_based_index = column_index - 1

    if zero_based_index >= len(row_values):
        return None

    return row_values[zero_based_index]


def normalize_date_value_by_header(
    row_values: tuple[object, ...],
    columns: Mapping[str, int],
    header_name: str,
    sheet_name: str,
    row_index: int,
) -> date | None:
    value = get_cell_value_by_header(row_values, columns, header_name)

    try:
        return normalize_date_value(value)
    except KpNormalizationError as exc:
        raise RowNormalizationSkipped(
            SourceRowIssue(
                sheet_name=sheet_name,
                row_index=row_index,
                column_name=header_name,
                raw_value=format_raw_value(value),
                reason=f"Не удалось распознать дату: {format_raw_value(value)}",
            )
        ) from exc


def normalize_kp_row(
    row_values: tuple[object, ...],
    row_index: int,
    columns: Mapping[str, int],
    sheet_name: str,
) -> NormalizedKpRow:
    return NormalizedKpRow(
        source_row_index=row_index,
        request_number=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "№ КП")
        ),
        received_date=normalize_date_value_by_header(
            row_values,
            columns,
            "Дата получения",
            sheet_name,
            row_index,
        ),
        manufacturer=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Производитель")
        ),
        branch=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Филиал")
        ),
        employee=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Сотрудник")
        ),
        email_subject=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Тема письма")
        ),
        proposal_deadline=normalize_date_value_by_header(
            row_values,
            columns,
            "Крайний срок предоставления предложения",
            sheet_name,
            row_index,
        ),
        preparation_status=normalize_text_value(
            get_cell_value_by_header(
                row_values,
                columns,
                "Статус подготовки КП",
            )
        ),
    )


def is_empty_kp_row(row: NormalizedKpRow) -> bool:
    return (
        row.request_number == ""
        and row.received_date is None
        and row.manufacturer == ""
        and row.branch == ""
        and row.employee == ""
        and row.email_subject == ""
        and row.proposal_deadline is None
        and row.preparation_status == ""
    )


def normalize_kp_rows(
    raw_sheets: RawSheets,
    raw_header_maps: RawHeaderMaps,
) -> KpNormalizationResult:
    kp_sheet = raw_sheets.kp_sheet
    kp_columns = raw_header_maps.kp_headers.columns

    normalized_rows: list[NormalizedKpRow] = []
    issues: list[SourceRowIssue] = []

    for row_index, row_values in enumerate(
        kp_sheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        try:
            normalized_row = normalize_kp_row(
                row_values=row_values,
                row_index=row_index,
                columns=kp_columns,
                sheet_name=kp_sheet.title,
            )
        except RowNormalizationSkipped as exc:
            issues.append(exc.issue)
            continue

        if is_empty_kp_row(normalized_row):
            continue

        normalized_rows.append(normalized_row)

    return KpNormalizationResult(rows=normalized_rows, issues=issues)
