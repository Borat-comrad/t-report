from __future__ import annotations

from datetime import date

from entity_mapper import DeliveryItem
from kp_analyzer import KpReportItem, build_request_state
from management_insights import BottleneckSummary, ManagerSummary
from weekly_report_models import BuiltWeeklyReport


def format_date_value(value: date | None) -> str:
    if value is None:
        return ""

    return value.strftime("%d.%m.%Y")


def format_float_value(value: float | None) -> str:
    if value is None:
        return ""

    return f"{value:.2f}"


def format_avg_value(value: float | None) -> str:
    if value is None:
        return ""

    return f"{value:.1f}"


def append_field(lines: list[str], label: str, value: str) -> None:
    if value == "":
        return

    lines.append(f"{label}: {value}")


def format_kp_item_block(item: KpReportItem) -> str:
    lines: list[str] = []

    append_field(lines, "Строка Excel (номер исходной строки)", str(item.source_row_index))
    append_field(lines, "№ запроса (идентификатор)", item.request_number)
    append_field(lines, "Дата получения (дд.мм.гггг)", format_date_value(item.received_date))
    append_field(lines, "Производитель (контрагент/бренд)", item.manufacturer)
    append_field(lines, "Филиал (зона процесса)", item.branch)
    append_field(lines, "Сотрудник (ответственный менеджер)", item.employee)
    append_field(lines, "Тема письма (краткое содержание запроса)", item.email_subject)
    append_field(
        lines,
        "Крайний срок предоставления предложения (дедлайн, дд.мм.гггг)",
        format_date_value(item.proposal_deadline),
    )
    append_field(lines, "Просрочка, дней (календарное отклонение от дедлайна)", str(item.overdue_days))
    append_field(lines, "Состояние запроса (текущий статус в отчете)", item.request_state or build_request_state(item.overdue_days))
    append_field(lines, "Статус подготовки КП (исходное поле Excel)", item.preparation_status)

    return "\n".join(lines)


def format_delivery_item_block(item: DeliveryItem) -> str:
    lines: list[str] = []

    append_field(lines, "Строка Excel (номер исходной строки)", str(item.source_row_index))
    append_field(lines, "Код (внутренний код позиции/заказа)", item.code)
    append_field(lines, "Дата получения заказа (дд.мм.гггг)", format_date_value(item.order_received_date))
    append_field(lines, "Номер РО (идентификатор заказа)", item.ro_number)
    append_field(lines, "Филиал (зона исполнения)", item.branch)
    append_field(lines, "Сумма, евро без НДС (EUR)", format_float_value(item.amount_eur_without_vat))
    append_field(lines, "Договор (привязка к договору)", item.contract)
    append_field(lines, "Ответственный (владелец поставки)", item.owner)
    append_field(lines, "Дата поставки (плановая дата, дд.мм.гггг)", format_date_value(item.delivery_date))
    append_field(lines, "Дата отгрузки факт (фактическая дата, дд.мм.гггг)", format_date_value(item.shipped_actual_date))

    return "\n".join(lines)


def format_manager_summary_block(item: ManagerSummary) -> str:
    lines: list[str] = []

    append_field(lines, "Менеджер (приоритетный флаг)", item.display_name)
    append_field(lines, "КП всего с просрочкой, шт.", str(item.overdue_kp_count))
    append_field(lines, "Критичные КП, шт.", str(item.critical_kp_count))
    append_field(lines, "КП 1–7 дней, шт.", str(item.warning_kp_count))
    append_field(lines, "Средняя просрочка, дни", format_avg_value(item.avg_overdue_days))
    if item.max_overdue_days is not None:
        append_field(lines, "Максимальная просрочка, дни", str(item.max_overdue_days))
    append_field(lines, "Поставки на текущую неделю, шт.", str(item.current_week_delivery_count))
    append_field(lines, "Поставки на следующие 2 недели, шт.", str(item.next_two_weeks_delivery_count))
    append_field(lines, "Индекс нагрузки, баллы", str(item.workload_score))
    append_field(lines, "Оценка нагрузки", item.load_status)
    append_field(lines, "Оценка эффективности", item.efficiency_assessment)
    append_field(lines, "Почему успевает/не успевает", item.bottleneck_reason)
    append_field(lines, "Проблемные производители", item.delayed_manufacturers)
    append_field(lines, "Проблемные филиалы", item.delayed_branches)

    return "\n".join(lines)


def format_bottleneck_block(item: BottleneckSummary) -> str:
    lines: list[str] = []

    append_field(lines, item.group_type, item.group_name)
    append_field(lines, "Просроченных КП, шт.", str(item.overdue_kp_count))
    append_field(lines, "Критичных КП, шт.", str(item.critical_kp_count))
    append_field(lines, "КП 1–7 дней, шт.", str(item.warning_kp_count))
    append_field(lines, "Средняя просрочка, дни", format_avg_value(item.avg_overdue_days))
    if item.max_overdue_days is not None:
        append_field(lines, "Максимальная просрочка, дни", str(item.max_overdue_days))
    append_field(lines, "Задействованные менеджеры", item.affected_managers)
    append_field(lines, "Диагностика", item.diagnostic_comment)

    return "\n".join(lines)


def build_section(title: str, items: list[str], empty_message: str = "Нет записей") -> str:
    lines = [title]

    if not items:
        lines.append(empty_message)
        return "\n".join(lines)

    lines.append(f"Количество записей: {len(items)}")
    lines.append("")
    lines.append("\n\n".join(items))

    return "\n".join(lines)


def build_report_text(report: BuiltWeeklyReport) -> str:
    summary = report.summary

    report_lines = [
        "Еженедельный отчёт по КП и поставкам",
        f"Дата отчёта: {format_date_value(summary.report_date)}",
        "",
        (
            "Сводка: "
            f"критичные КП={summary.critical_kp_count}, "
            f"КП 1–7 дней={summary.warning_kp_count}, "
            f"поставки на текущую неделю={summary.current_week_delivery_count}, "
            f"поставки на следующие 2 недели={summary.next_two_weeks_delivery_count}, "
            f"менеджеров в зоне контроля={len(report.manager_summaries)}"
        ),
        "",
        build_section(
            "Сводка по каждому менеджеру",
            [format_manager_summary_block(item) for item in report.manager_summaries],
            empty_message="Менеджеры в зоне контроля не выявлены",
        ),
        "",
        build_section(
            "Косвенные узкие места по производителям",
            [format_bottleneck_block(item) for item in report.manufacturer_bottlenecks[:10]],
            empty_message="Косвенные узкие места по производителям не выявлены",
        ),
        "",
        build_section(
            "Косвенные узкие места по филиалам",
            [format_bottleneck_block(item) for item in report.branch_bottlenecks[:10]],
            empty_message="Косвенные узкие места по филиалам не выявлены",
        ),
        "",
        build_section(
            "Критическая просрочка по предоставлению предложения",
            [format_kp_item_block(item) for item in report.critical_kp_items],
        ),
        "",
        build_section(
            "Просрочка по предоставлению предложения (1–7 дней)",
            [format_kp_item_block(item) for item in report.warning_kp_items],
        ),
        "",
        build_section(
            "Поставки на текущую неделю",
            [format_delivery_item_block(item) for item in report.current_week_delivery_items],
        ),
        "",
        build_section(
            "Поставки на следующие 2 недели",
            [format_delivery_item_block(item) for item in report.next_two_weeks_delivery_items],
        ),
    ]

    return "\n".join(report_lines)
