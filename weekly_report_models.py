from dataclasses import dataclass
from datetime import date

from data_quality import SourceRowIssue
from entity_mapper import DeliveryItem
from kp_analyzer import KpReportItem
from management_insights import BottleneckSummary, ManagerSummary


@dataclass(frozen=True)
class WeeklyReportSummary:
    report_date: date
    critical_kp_count: int
    warning_kp_count: int
    current_week_delivery_count: int
    next_two_weeks_delivery_count: int


@dataclass(frozen=True)
class BuiltWeeklyReport:
    summary: WeeklyReportSummary
    critical_kp_items: list[KpReportItem]
    warning_kp_items: list[KpReportItem]
    current_week_delivery_items: list[DeliveryItem]
    next_two_weeks_delivery_items: list[DeliveryItem]
    manager_summaries: list[ManagerSummary]
    manufacturer_bottlenecks: list[BottleneckSummary]
    branch_bottlenecks: list[BottleneckSummary]
    source_row_issues: list[SourceRowIssue]
