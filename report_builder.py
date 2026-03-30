from datetime import date

from delivery_analyzer import DeliveryAnalysisResult
from entity_mapper import DeliveryItem
from kp_analyzer import KpAnalysisResult, KpReportItem
from report_context_factory import ReportContext


def format_date_value(value: date | None) -> str:
    if value is None:
        return ""

    return value.strftime("%d.%m.%Y")


def format_float_value(value: float | None) -> str:
    if value is None:
        return ""

    return f"{value:.2f}"


def append_field(lines: list[str], label: str, value: str) -> None:
    if value == "":
        return

    lines.append(f"{label}: {value}")


def format_kp_item_block(item: KpReportItem) -> str:
    lines: list[str] = []

    append_field(lines, "Строка Excel", str(item.source_row_index))
    append_field(lines, "№", item.request_number)
    append_field(lines, "Дата получения", format_date_value(item.received_date))
    append_field(lines, "Производитель", item.manufacturer)
    append_field(lines, "Филиал", item.branch)
    append_field(lines, "Сотрудник", item.employee)
    append_field(lines, "Тема письма", item.email_subject)
    append_field(
        lines,
        "Крайний срок предоставления предложения",
        format_date_value(item.proposal_deadline),
    )
    append_field(lines, "Просрочка, дней", str(item.overdue_days))
    append_field(lines, "Статус подготовки КП", item.preparation_status)

    return "\n".join(lines)


def format_delivery_item_block(item: DeliveryItem) -> str:
    lines: list[str] = []

    append_field(lines, "Строка Excel", str(item.source_row_index))
    append_field(lines, "Код", item.code)
    append_field(lines, "Дата получения заказа", format_date_value(item.order_received_date))
    append_field(lines, "Номер РО", item.ro_number)
    append_field(lines, "Филиал", item.branch)
    append_field(lines, "Сумма, евро без НДС", format_float_value(item.amount_eur_without_vat))
    append_field(lines, "Договор", item.contract)
    append_field(lines, "Ответственный", item.owner)
    append_field(lines, "Дата поставки", format_date_value(item.delivery_date))
    append_field(lines, "Дата отгрузки факт", format_date_value(item.shipped_actual_date))

    return "\n".join(lines)


def build_section(title: str, items: list[str]) -> str:
    lines = [title]

    if not items:
        lines.append("Нет записей")
        return "\n".join(lines)

    lines.append(f"Количество записей: {len(items)}")
    lines.append("")
    lines.append("\n\n".join(items))

    return "\n".join(lines)


def build_report_text(
    context: ReportContext,
    kp_result: KpAnalysisResult,
    delivery_result: DeliveryAnalysisResult,
) -> str:
    report_lines = [
        "Еженедельный отчёт по КП и поставкам",
        f"Дата отчёта: {format_date_value(context.report_date)}",
        "",
        (
            "Сводка: "
            f"критичные КП={len(kp_result.critical_overdue_items)}, "
            f"КП 1–7 дней={len(kp_result.overdue_items)}, "
            f"поставки на текущую неделю={len(delivery_result.current_week_items)}, "
            f"поставки на следующие 2 недели={len(delivery_result.next_two_weeks_items)}"
        ),
        "",
        build_section(
            "Критическая просрочка по предоставлению предложения",
            [format_kp_item_block(item) for item in kp_result.critical_overdue_items],
        ),
        "",
        build_section(
            "Просрочка по предоставлению предложения (1–7 дней)",
            [format_kp_item_block(item) for item in kp_result.overdue_items],
        ),
        "",
        build_section(
            "Поставки на текущую неделю",
            [format_delivery_item_block(item) for item in delivery_result.current_week_items],
        ),
        "",
        build_section(
            "Поставки на следующие 2 недели",
            [format_delivery_item_block(item) for item in delivery_result.next_two_weeks_items],
        ),
    ]

    return "\n".join(report_lines)
