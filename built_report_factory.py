from datetime import date

from data_quality import SourceRowIssue
from entity_mapper import DeliveryItem
from kp_analyzer import KpReportItem
from management_insights import build_management_insights
from weekly_report_models import BuiltWeeklyReport, WeeklyReportSummary


def build_weekly_report(
    report_date: date,
    critical_kp_items: list[KpReportItem],
    warning_kp_items: list[KpReportItem],
    current_week_delivery_items: list[DeliveryItem],
    next_two_weeks_delivery_items: list[DeliveryItem],
    source_row_issues: list[SourceRowIssue] | None = None,
) -> BuiltWeeklyReport:
    summary = WeeklyReportSummary(
        report_date=report_date,
        critical_kp_count=len(critical_kp_items),
        warning_kp_count=len(warning_kp_items),
        current_week_delivery_count=len(current_week_delivery_items),
        next_two_weeks_delivery_count=len(next_two_weeks_delivery_items),
    )

    insights = build_management_insights(
        critical_kp_items=critical_kp_items,
        warning_kp_items=warning_kp_items,
        current_week_delivery_items=current_week_delivery_items,
        next_two_weeks_delivery_items=next_two_weeks_delivery_items,
    )

    return BuiltWeeklyReport(
        summary=summary,
        critical_kp_items=critical_kp_items,
        warning_kp_items=warning_kp_items,
        current_week_delivery_items=current_week_delivery_items,
        next_two_weeks_delivery_items=next_two_weeks_delivery_items,
        manager_summaries=insights.manager_summaries,
        manufacturer_bottlenecks=insights.manufacturer_bottlenecks,
        branch_bottlenecks=insights.branch_bottlenecks,
        source_row_issues=[] if source_row_issues is None else source_row_issues,
    )
