from dataclasses import dataclass
from typing import Mapping

from openpyxl.worksheet.worksheet import Worksheet

from exel_sourse_reader import RawSheets


class StructureValidationError(Exception):
    pass


KP_REQUIRED_HEADERS = (
    "№",
    "Дата получения",
    "Производитель",
    "Филиал",
    "Сотрудник",
    "Тема письма",
    "Крайний срок предоставления предложения",
    "Статус подготовки КП",
)

# Для срочной демки контракт листа поставок выровнен под реальный DS.xlsx.
# Первый столбец в файле не имеет заголовка, поэтому как обязательный он здесь не проверяется.
DELIVERY_REQUIRED_HEADERS = (
    "дата получения заказа",
    "номер РО",
    "Филиал",
    "сумма, евро без НДС",
    "Договор",
    "Ответственный",
    "Дата поставки",
    "Дата отгрузки факт",
)


@dataclass(frozen=True)
class SheetHeaderMap:
    sheet_name: str
    columns: Mapping[str, int]


@dataclass(frozen=True)
class RawHeaderMaps:
    kp_headers: SheetHeaderMap
    delivery_headers: SheetHeaderMap


def normalize_header_value(value: object) -> str:
    if value is None:
        return ""

    return str(value).strip()


def build_header_map(sheet: Worksheet) -> SheetHeaderMap:
    header_row = next(
        sheet.iter_rows(min_row=1, max_row=1, values_only=True),
        (),
    )

    if not header_row:
        raise StructureValidationError(
            f"В листе '{sheet.title}' отсутствует строка заголовков."
        )

    columns: dict[str, int] = {}

    for column_index, cell_value in enumerate(header_row, start=1):
        header_name = normalize_header_value(cell_value)

        if header_name == "":
            continue

        columns[header_name] = column_index

    return SheetHeaderMap(
        sheet_name=sheet.title,
        columns=columns,
    )


def validate_required_headers(
    header_map: SheetHeaderMap,
    required_headers: tuple[str, ...],
) -> None:
    missing_headers = [
        header_name
        for header_name in required_headers
        if header_name not in header_map.columns
    ]

    if missing_headers:
        missing_headers_text = ", ".join(missing_headers)
        raise StructureValidationError(
            f"В листе '{header_map.sheet_name}' отсутствуют "
            f"обязательные колонки: {missing_headers_text}"
        )


def validate_raw_sheets_structure(raw_sheets: RawSheets) -> RawHeaderMaps:
    kp_headers = build_header_map(raw_sheets.kp_sheet)
    delivery_headers = build_header_map(raw_sheets.delivery_sheet)

    validate_required_headers(kp_headers, KP_REQUIRED_HEADERS)
    validate_required_headers(delivery_headers, DELIVERY_REQUIRED_HEADERS)

    return RawHeaderMaps(
        kp_headers=kp_headers,
        delivery_headers=delivery_headers,
    )
