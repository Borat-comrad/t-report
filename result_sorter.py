from delivery_analyzer import DeliveryAnalysisResult
from kp_analyzer import KpAnalysisResult


def sort_kp_analysis_result(result: KpAnalysisResult) -> KpAnalysisResult:
    critical_overdue_items = sorted(
        result.critical_overdue_items,
        key=lambda item: (
            -item.overdue_days,
            item.proposal_deadline,
            item.request_number,
        ),
    )

    overdue_items = sorted(
        result.overdue_items,
        key=lambda item: (
            -item.overdue_days,
            item.proposal_deadline,
            item.request_number,
        ),
    )

    return KpAnalysisResult(
        critical_overdue_items=critical_overdue_items,
        overdue_items=overdue_items,
    )


def sort_delivery_analysis_result(
    result: DeliveryAnalysisResult,
) -> DeliveryAnalysisResult:
    current_week_items = sorted(
        result.current_week_items,
        key=lambda item: (
            item.delivery_date,
            item.ro_number,
        ),
    )

    next_two_weeks_items = sorted(
        result.next_two_weeks_items,
        key=lambda item: (
            item.delivery_date,
            item.ro_number,
        ),
    )

    return DeliveryAnalysisResult(
        current_week_items=current_week_items,
        next_two_weeks_items=next_two_weeks_items,
    )
