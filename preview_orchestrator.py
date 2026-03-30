from pathlib import Path

from delivery_analyzer import analyze_delivery_items
from delivery_normalizer import normalize_delivery_rows
from entity_mapper import map_delivery_rows, map_kp_rows
from exel_sourse_reader import load_required_sheets
from kp_analyzer import analyze_kp_items
from kp_normalizer import normalize_kp_rows
from report_builder import build_report_text
from report_context_factory import ReportContext
from result_sorter import sort_delivery_analysis_result, sort_kp_analysis_result
from structure_validator import validate_raw_sheets_structure


def run_preview_pipeline(excel_path: Path, context: ReportContext) -> str:
    raw_sheets = load_required_sheets(excel_path)
    raw_header_maps = validate_raw_sheets_structure(raw_sheets)

    normalized_kp_rows = normalize_kp_rows(raw_sheets, raw_header_maps)
    normalized_delivery_rows = normalize_delivery_rows(raw_sheets, raw_header_maps)

    kp_items = map_kp_rows(normalized_kp_rows)
    delivery_items = map_delivery_rows(normalized_delivery_rows)

    kp_analysis = analyze_kp_items(kp_items, context.report_date)
    delivery_analysis = analyze_delivery_items(delivery_items, context)

    sorted_kp_analysis = sort_kp_analysis_result(kp_analysis)
    sorted_delivery_analysis = sort_delivery_analysis_result(delivery_analysis)

    return build_report_text(
        context=context,
        kp_result=sorted_kp_analysis,
        delivery_result=sorted_delivery_analysis,
    )
