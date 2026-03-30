from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class ExcelSourceError(Exception):
    pass


@dataclass(frozen=True)
class RawSheets:
    kp_sheet: Worksheet
    delivery_sheet: Worksheet


def load_excel_workbook(excel_path: Path) -> Workbook:
    if not excel_path.exists():
        raise ExcelSourceError(f"Excel-файл не найден: {excel_path}")

    try:
        return load_workbook(excel_path)
    except Exception as exc:
        raise ExcelSourceError(
            f"Не удалось открыть Excel-файл: {excel_path}"
        ) from exc


def get_required_sheet(workbook: Workbook, sheet_name: str) -> Worksheet:
    if sheet_name not in workbook.sheetnames:
        raise ExcelSourceError(f"Лист не найден в Excel-книге: {sheet_name}")

    return workbook[sheet_name]


def load_required_sheets(excel_path: Path) -> RawSheets:
    workbook = load_excel_workbook(excel_path)

    kp_sheet = get_required_sheet(workbook, "КП")
    delivery_sheet = get_required_sheet(workbook, "Поставки")

    return RawSheets(
        kp_sheet=kp_sheet,
        delivery_sheet=delivery_sheet,
    )