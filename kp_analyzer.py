from dataclasses import dataclass
from datetime import date

from entity_mapper import KpItem


@dataclass(frozen=True)
class KpReportItem:
    source_row_index: int
    request_number: str
    received_date: date | None
    manufacturer: str
    branch: str
    employee: str
    email_subject: str
    proposal_deadline: date
    preparation_status: str
    overdue_days: int


@dataclass(frozen=True)
class KpAnalysisResult:
    critical_overdue_items: list[KpReportItem]
    overdue_items: list[KpReportItem]


def is_empty_status(status: str) -> bool:
    return status.strip() == ""


def analyze_kp_items(items: list[KpItem], report_date: date) -> KpAnalysisResult:
    critical_overdue_items: list[KpReportItem] = []
    overdue_items: list[KpReportItem] = []

    for item in items:
        if not is_empty_status(item.preparation_status):
            continue

        if item.proposal_deadline is None:
            continue

        overdue_days = (report_date - item.proposal_deadline).days

        if overdue_days <= 0:
            continue

        report_item = KpReportItem(
            source_row_index=item.source_row_index,
            request_number=item.request_number,
            received_date=item.received_date,
            manufacturer=item.manufacturer,
            branch=item.branch,
            employee=item.employee,
            email_subject=item.email_subject,
            proposal_deadline=item.proposal_deadline,
            preparation_status=item.preparation_status,
            overdue_days=overdue_days,
        )

        if overdue_days > 7:
            critical_overdue_items.append(report_item)
        else:
            overdue_items.append(report_item)

    return KpAnalysisResult(
        critical_overdue_items=critical_overdue_items,
        overdue_items=overdue_items,
    )
