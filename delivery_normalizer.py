from dataclasses import dataclass
from datetime import date
from typing import Mapping

from data_quality import RowNormalizationSkipped, SourceRowIssue, format_raw_value
from exel_sourse_reader import RawSheets
from kp_normalizer import normalize_date_value, normalize_text_value
from structure_validator import RawHeaderMaps


class DeliveryNormalizationError(Exception):
    pass


@dataclass(frozen=True)
class NormalizedDeliveryRow:
    source_row_index: int
    code: str
    order_received_date: date | None
    ro_number: str
    branch: str
    amount_eur_without_vat: float | None
    contract: str
    owner: str
    delivery_date: date | None
    shipped_actual_date: date | None


@dataclass(frozen=True)
class DeliveryNormalizationResult:
    rows: list[NormalizedDeliveryRow]
    issues: list[SourceRowIssue]


def normalize_float_value(value: object) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text_value = normalize_text_value(value).replace(" ", "")

    if text_value == "":
        return None

    if "," in text_value and "." in text_value:
        if text_value.rfind(",") > text_value.rfind("."):
            text_value = text_value.replace(".", "").replace(",", ".")
        else:
            text_value = text_value.replace(",", "")
    else:
        text_value = text_value.replace(",", ".")

    try:
        return float(text_value)
    except ValueError as exc:
        raise DeliveryNormalizationError(
            f"Не удалось распознать число: {text_value}"
        ) from exc


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
    except Exception as exc:
        raise RowNormalizationSkipped(
            SourceRowIssue(
                sheet_name=sheet_name,
                row_index=row_index,
                column_name=header_name,
                raw_value=format_raw_value(value),
                reason=f"Не удалось распознать дату: {format_raw_value(value)}",
            )
        ) from exc


def normalize_float_value_by_header(
    row_values: tuple[object, ...],
    columns: Mapping[str, int],
    header_name: str,
    sheet_name: str,
    row_index: int,
) -> float | None:
    value = get_cell_value_by_header(row_values, columns, header_name)

    try:
        return normalize_float_value(value)
    except DeliveryNormalizationError as exc:
        raise RowNormalizationSkipped(
            SourceRowIssue(
                sheet_name=sheet_name,
                row_index=row_index,
                column_name=header_name,
                raw_value=format_raw_value(value),
                reason=f"Не удалось распознать сумму: {format_raw_value(value)}",
            )
        ) from exc


# Для текущего DS.xlsx первый столбец поставок физически существует,
# но его заголовок пустой. Для демо читаем его по физической позиции 1.
def get_delivery_code_value(row_values: tuple[object, ...]) -> object:
    if not row_values:
        return None

    return row_values[0]


def normalize_delivery_row(
    row_values: tuple[object, ...],
    row_index: int,
    columns: Mapping[str, int],
    sheet_name: str,
) -> NormalizedDeliveryRow:
    return NormalizedDeliveryRow(
        source_row_index=row_index,
        code=normalize_text_value(get_delivery_code_value(row_values)),
        order_received_date=normalize_date_value_by_header(
            row_values,
            columns,
            "дата получения заказа",
            sheet_name,
            row_index,
        ),
        ro_number=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "номер РО")
        ),
        branch=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Филиал")
        ),
        amount_eur_without_vat=normalize_float_value_by_header(
            row_values,
            columns,
            "сумма, евро без НДС",
            sheet_name,
            row_index,
        ),
        contract=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Договор")
        ),
        owner=normalize_text_value(
            get_cell_value_by_header(row_values, columns, "Ответственный")
        ),
        delivery_date=normalize_date_value_by_header(
            row_values,
            columns,
            "Дата поставки",
            sheet_name,
            row_index,
        ),
        shipped_actual_date=normalize_date_value_by_header(
            row_values,
            columns,
            "Дата отгрузки факт",
            sheet_name,
            row_index,
        ),
    )


def is_empty_delivery_row(row: NormalizedDeliveryRow) -> bool:
    return (
        row.code == ""
        and row.order_received_date is None
        and row.ro_number == ""
        and row.branch == ""
        and row.amount_eur_without_vat is None
        and row.contract == ""
        and row.owner == ""
        and row.delivery_date is None
        and row.shipped_actual_date is None
    )


def normalize_delivery_rows(
    raw_sheets: RawSheets,
    raw_header_maps: RawHeaderMaps,
) -> DeliveryNormalizationResult:
    delivery_sheet = raw_sheets.delivery_sheet
    delivery_columns = raw_header_maps.delivery_headers.columns

    normalized_rows: list[NormalizedDeliveryRow] = []
    issues: list[SourceRowIssue] = []

    for row_index, row_values in enumerate(
        delivery_sheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        try:
            normalized_row = normalize_delivery_row(
                row_values=row_values,
                row_index=row_index,
                columns=delivery_columns,
                sheet_name=delivery_sheet.title,
            )
        except RowNormalizationSkipped as exc:
            issues.append(exc.issue)
            continue

        if is_empty_delivery_row(normalized_row):
            continue

        normalized_rows.append(normalized_row)

    return DeliveryNormalizationResult(rows=normalized_rows, issues=issues)
